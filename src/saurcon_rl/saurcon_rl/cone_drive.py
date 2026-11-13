#!/usr/bin/env python3
"""Drive a cone-vision policy in MuJoCo from rendered camera pixels.

Each 50 ms control step renders the car's OAK-D-like colour and depth images,
runs cones.ConeDetector on them, and feeds the detections (no map, no
localization) to the policy. Also measures the real detector against the true
cones, which checks the simulated detector the policy was trained with.

--model classical drives with the classical cone follower (saurcon_rl.cone_follower)
instead of a learned policy; the video then also shows its centreline path (green).

usage: MUJOCO_GL=egl python -m saurcon_rl.cone_drive --model rl_runs/cones_v1/best_model.zip
           [--detector render|sim] [--laps 2] [--track 0] [--video out.mp4] [--json out.json]
"""
import argparse
import json
import math

import cv2
import mujoco
import numpy as np

from .cone_env import CAMERA_X, MAX_RANGE, ConeMemory, MujocoConeEnv, encode, visible_cones
from .cones import ConeDetector
from .env import load_tracks
from .train import race_start_s

W, H, HFOV = 640, 400, 1.204
CAMERA_HEIGHT = 0.137
FX = (W / 2) / math.tan(HFOV / 2)


def mujoco_detector():
    # MuJoCo cones render red-orange (hue ~7) and there are no orange racks to reject.
    return ConeDetector(FX, FX, W / 2, H / 2, hsv_lo=(0, 150, 40), hsv_hi=(14, 255, 255), camera_height=0.137)


def detect_from_pixels(renderer, data, detector):
    renderer.update_scene(data, camera='oak_rgb'); rgb = renderer.render()
    renderer.enable_depth_rendering(); renderer.update_scene(data, camera='oak_rgb')
    depth = renderer.render(); renderer.disable_depth_rendering()
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    dets = detector.detect(bgr, depth)
    # optical frame (x right, y down, z forward) -> base_link (x forward, y left)
    pts = np.array([[CAMERA_X + d.p_cam[2], -d.p_cam[0]] for d in dets]).reshape(-1, 2)
    return pts, bgr, dets


def draw_path(bgr, follower):
    """Project the follower's path (base_link, on the floor) into the onboard image."""
    pts = []
    for bx, by in follower.path:
        Z = bx - CAMERA_X
        if Z > 0.25:
            pts.append((int(W / 2 + FX * (-by) / Z), int(H / 2 + FX * CAMERA_HEIGHT / Z)))
    for a, b in zip(pts, pts[1:]):
        cv2.line(bgr, a, b, (60, 220, 60), 2)
    if follower.target is not None and follower.target[0] - CAMERA_X > 0.25:
        Z = follower.target[0] - CAMERA_X
        cv2.circle(bgr, (int(W / 2 + FX * (-follower.target[1]) / Z), int(H / 2 + FX * CAMERA_HEIGHT / Z)), 7, (60, 220, 60), -1)


def run(model_path, detector_mode='render', laps=2, track=0, video=None, max_time=60.0, seed=None):
    follower = policy = None
    if model_path == 'classical':
        from .cone_follower import ConeFollower
        follower = ConeFollower()
    else:
        from stable_baselines3 import PPO
        policy = PPO.load(model_path, device='cpu')
    env = MujocoConeEnv(load_tracks(), randomize=False, max_time=max_time, cone_mode='visual', seed=seed)
    obs, _ = env.reset(options={'track': track, 'start_s': race_start_s(env.tracks[track])})
    renderer = mujoco.Renderer(env.m, H, W); chase = mujoco.Renderer(env.m, H, W) if video else None
    detector = mujoco_detector()
    mem = ConeMemory()
    writer = cv2.VideoWriter(video, cv2.VideoWriter_fourcc(*'avc1'), 20, (2 * W, H)) if video else None
    errs, misses, false_pos, seen = [], 0, 0, 0
    info = {}
    while True:
        if detector_mode == 'render':
            pts, bgr, dets = detect_from_pixels(renderer, env.d, detector)
            truth = visible_cones(env.track.cones, env.x, env.y, env.yaw, noise=False)
            truth = truth[np.hypot(truth[:, 0] - CAMERA_X, truth[:, 1]) < MAX_RANGE * 0.9]
            used = set()
            for p in pts:
                d = np.hypot(*(truth - p).T) if len(truth) else np.array([])
                j = int(np.argmin(d)) if len(d) else -1
                if j >= 0 and d[j] < 0.3 and j not in used:
                    used.add(j); errs.append(d[j])
                else:
                    false_pos += 1
            misses += len(truth) - len(used); seen += len(truth)
            c, sn = math.cos(env.yaw), math.sin(env.yaw)
            mem.update(np.column_stack([env.x + c * pts[:, 0] - sn * pts[:, 1], env.y + sn * pts[:, 0] + c * pts[:, 1]]), env.t)
            rel, ages = mem.relative(env.x, env.y, env.yaw, env.t)
            obs = encode(rel, env.v, env.state[4], env.steer, env.prev_action, ages)
            if follower is not None:
                action = follower.action(rel, env.v, env.state[4])
            if writer is not None:
                if follower is not None:
                    draw_path(bgr, follower)
                for d in dets:
                    cv2.circle(bgr, (int(d.u), int(d.v)), 6, (255, 200, 0), 2)
                    cv2.putText(bgr, f'{d.range:.1f}', (int(d.u) - 10, int(d.v) + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                chase.update_scene(env.d, camera='chase')
                frame = np.hstack([bgr, cv2.cvtColor(chase.render(), cv2.COLOR_RGB2BGR)])
                cv2.putText(frame, f't {env.t:5.2f}s  v {env.v:4.1f} m/s  laps {len(env.lap_times)}', (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                writer.write(frame)
        else:
            if follower is not None:
                rel, _ = env.memory.relative(env.x, env.y, env.yaw, env.t)
                action = follower.action(rel, env.v, env.state[4])
        if detector_mode != 'render' and writer is not None:
            # Simulated detector (as trained): show the policy's cone memory projected into the
            # onboard camera (cyan = seen this step, orange = remembered), next to the chase view.
            renderer.update_scene(env.d, camera='oak_rgb')
            bgr = cv2.cvtColor(renderer.render(), cv2.COLOR_RGB2BGR)
            rel, ages = env.memory.relative(env.x, env.y, env.yaw, env.t)
            for (bx, by), age in zip(rel, ages):
                Z = bx - CAMERA_X
                if Z < 0.3:
                    continue
                u, v = W / 2 + FX * (-by) / Z, H / 2 + FX * CAMERA_HEIGHT / Z
                if 0 <= u < W and 0 <= v < H:
                    cv2.circle(bgr, (int(u), int(v)), 6, (255, 200, 0) if age < 0.06 else (0, 140, 255), 2)
            if follower is not None:
                draw_path(bgr, follower)
            behind = int(np.sum(rel[:, 0] - CAMERA_X < 0.3)) if len(rel) else 0
            chase.update_scene(env.d, camera='chase')
            frame = np.hstack([bgr, cv2.cvtColor(chase.render(), cv2.COLOR_RGB2BGR)])
            cv2.putText(frame, f't {env.t:5.2f}s  v {env.v:4.1f} m/s  laps {len(env.lap_times)}  '
                               f'remembered cones {len(rel)} ({behind} beside/behind)', (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
            writer.write(frame)
        if policy is not None:
            action, _ = policy.predict(obs, deterministic=True)
        obs, _, term, trunc, info = env.step(action)
        if term or trunc or info['laps'] >= laps:
            break
    if writer is not None:
        writer.release()
    t = info.get('lap_times', [])
    res = {'detector': detector_mode, 'laps': len(t), 'crashed': bool(info.get('crashed')),
           'standing_lap_s': round(t[0], 3) if t else None,
           'flying_lap_s': round(t[1] - t[0], 3) if len(t) > 1 else None,
           'progress_m': round(info.get('progress', 0.0), 1)}
    if detector_mode == 'render':
        res.update({'detections_matched': len(errs), 'position_error_rms_m': round(float(np.sqrt(np.mean(np.square(errs)))), 3) if errs else None,
                    'miss_rate': round(misses / max(seen, 1), 3), 'false_positives': false_pos})
    return res


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True, help="policy .zip, or 'classical' for the classical cone follower")
    p.add_argument('--detector', choices=['render', 'sim'], default='render')
    p.add_argument('--laps', type=int, default=2)
    p.add_argument('--track', type=int, default=0)
    p.add_argument('--video')
    p.add_argument('--json')
    p.add_argument('--seed', type=int, help='detector randomness (missed cones, noise)')
    a = p.parse_args()
    res = run(a.model, a.detector, a.laps, a.track, a.video, seed=a.seed)
    print(json.dumps(res, indent=1))
    if a.json:
        json.dump(res, open(a.json, 'w'), indent=1)


if __name__ == '__main__':
    main()
