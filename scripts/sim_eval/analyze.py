#!/usr/bin/env python3
"""Score timestamped poses against truth; optionally align only the first pose."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load(path, kind):
    samples = {}
    with open(path / 'log.csv') as f:
        for row in csv.reader(f):
            if len(row) > 4 and row[1] == kind:
                samples[float(row[0])] = [float(v) for v in row[2:5]]
    return np.array([[t] + samples[t] for t in sorted(samples)], dtype=float).reshape(-1, 4)


def score(gt, pose, align=False):
    pose = pose[(pose[:, 0] >= gt[0, 0]) & (pose[:, 0] <= gt[-1, 0])].copy()
    if not len(pose): raise ValueError('No overlapping pose and ground-truth samples')
    truth = np.column_stack([np.interp(pose[:, 0], gt[:, 0], gt[:, i] if i<3 else np.unwrap(gt[:, i])) for i in range(1,4)])
    if align:
        angle = truth[0, 2] - pose[0, 3]
        rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        pose[:, 1:3] = (pose[:, 1:3]-pose[0, 1:3]) @ rot.T + truth[0, :2]
        pose[:, 3] += angle
    error = np.linalg.norm(pose[:, 1:3]-truth[:, :2], axis=1)
    heading = np.degrees(np.arctan2(np.sin(pose[:, 3]-truth[:, 2]), np.cos(pose[:, 3]-truth[:, 2])))
    return pose, error, heading


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('runs', type=Path, nargs='+');p.add_argument('--kind', default='nav', choices=['nav','map'])
    p.add_argument('--alignment-from', type=Path, help='Mapping run used to fix map-to-world transform for localization')
    p.add_argument('--video', action='store_true');p.add_argument('--align', action='store_true');p.add_argument('--duration', type=float, default=47)
    p.add_argument('--output', type=Path, default=Path('evaluation/comparison'))
    a=p.parse_args()
    if a.align and a.alignment_from: p.error('Choose --align or --alignment-from')
    fixed=None
    if a.alignment_from:
        ref_gt=load(a.alignment_from,'gt');ref_pose=load(a.alignment_from,'map')
        first=ref_pose[(ref_pose[:,0]>=ref_gt[0,0])&(ref_pose[:,0]<=ref_gt[-1,0])][0]
        truth=np.array([np.interp(first[0],ref_gt[:,0],ref_gt[:,i] if i<3 else np.unwrap(ref_gt[:,i])) for i in range(1,4)])
        angle=truth[2]-first[3]
        rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        fixed=(rot,truth[:2]-rot@first[1:3],angle)
    a.output.mkdir(parents=True,exist_ok=True)
    fig, axes=plt.subplots(1,2,figsize=(12,5));results={}
    for path in a.runs:
        gt=load(path,'gt');pose=load(path,a.kind)
        if len(gt)<2 or not len(pose): raise ValueError(f'{path}: missing ground truth or {a.kind} poses')
        speed=np.linalg.norm(np.diff(gt[:,1:3],axis=0),axis=1)/np.maximum(np.diff(gt[:,0]),1e-6)
        moving=np.flatnonzero(speed>.15)
        if not len(moving): raise ValueError(f'{path}: vehicle never moved')
        t0=gt[moving[0],0]
        if fixed is not None:
            rot,translation,angle=fixed
            pose[:,1:3]=pose[:,1:3]@rot.T+translation;pose[:,3]+=angle
        # Align using the initial shared pose, then score only the requested lap window.
        pose,err,heading=score(gt,pose,a.align)
        m=(pose[:,0]>=t0)&(pose[:,0]<=t0+a.duration)
        if not m.any(): raise ValueError('No samples during lap')
        results[path.name]={'position_rms_m':float(np.sqrt(np.mean(err[m]**2))), 'position_max_m':float(err[m].max()),
                            'position_end_m':float(err[m][-1]), 'heading_rms_deg':float(np.sqrt(np.mean(heading[m]**2))),
                            'samples':int(m.sum()), 'largest_gap_s':float(np.diff(pose[m,0]).max()) if m.sum()>1 else 0.0,
                            'observed_duration_s':float(np.diff(pose[m,0])[np.diff(pose[m,0])<=.25].sum()),
                            'scored_duration_s':float(pose[m,0][-1]-pose[m,0][0]), 'alignment':str(a.alignment_from) if fixed is not None else ('first shared pose' if a.align else 'none')}
        axes[0].plot(pose[m,1],pose[m,2],label=path.name)
        gm=(gt[:,0]>=t0)&(gt[:,0]<=t0+a.duration);axes[0].plot(gt[gm,1],gt[gm,2],'k--',alpha=.4)
        axes[1].plot(pose[m,0]-t0,err[m],label=path.name)
        if a.video:
            import cv2
            frames=[]
            with (path/'log.csv').open() as f:
                for row in csv.reader(f):
                    if len(row)>2 and row[1]=='frame' and t0<=float(row[0])<=t0+a.duration:
                        frames.append((float(row[0]),int(row[2])))
            writer=cv2.VideoWriter(str(a.output/(path.name+'.mp4')),cv2.VideoWriter_fourcc(*'mp4v'),15,(640,400))
            if not writer.isOpened():raise RuntimeError('Video codec unavailable')
            for stamp,index in frames:
                image=cv2.imread(str(path/'frames'/f'{index:06d}.jpg'))
                if image is None:continue
                image=cv2.resize(image,(640,400))
                value=np.interp(stamp,pose[:,0],err)
                cv2.putText(image,f't={stamp-t0:.1f}s  error={value:.3f}m',(10,25),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,255,255),2)
                writer.write(image)
            writer.release()
    axes[0].axis('equal');axes[0].set(xlabel='x (m)',ylabel='y (m)');axes[1].set(xlabel='simulation/recorded time since motion (s)',ylabel='position error (m)')
    for ax in axes: ax.legend();ax.grid(True)
    fig.tight_layout();fig.savefig(a.output/'comparison.png')
    (a.output/'metrics.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))


if __name__=='__main__':main()
