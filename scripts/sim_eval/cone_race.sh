#!/bin/bash
# Gazebo race driven by the classical cone follower (saurcon_plan): camera -> detector -> follower -> /auto_cmd.
# usage: scripts/sim_eval/cone_race.sh <name> [laps] [extra launch args...]
#   e.g. scripts/sim_eval/cone_race.sh classical_slam 3 \
#          world:=$PWD/evaluation/worlds/no_markers.world slam:=true cone_mapping:=rtab
# (A leading "classical" argument, from the older <model> <name> form, is accepted and ignored.)
# Output: evaluation/cones_gz/<name>/ (deleted first) with log.csv, frames, chase camera (CHASE=1, the
# default here), launch.log, and follower.csv (the follower's state and waypoints, for the video).
# Then: .venv-rl/bin/python scripts/sim_eval/make_race_video.py evaluation/cones_gz/<name> out.mp4

WS=$(cd "$(dirname "$0")/../.." && pwd); cd "$WS"; source /opt/ros/jazzy/setup.bash
[ "${1:-}" = classical ] && shift
NAME=$1; LAPS=${2:-3}; shift $(( $# < 2 ? $# : 2 ))
OUT=$WS/evaluation/cones_gz/$NAME; rm -rf "$OUT"; mkdir -p "$(dirname "$OUT")"
CHASE=${CHASE:-1} DRIVER=race_driver.py RACE_LAPS=$LAPS RACE_TIMEOUT=150 timeout 600 bash scripts/sim_eval/runsim.sh "$WS" "$OUT" \
  use_aruco:=false slam:=false cone_follower:=true cone_debug_csv:="$OUT/follower.csv" "$@" > "$OUT.out" 2>&1
tail -1 "$OUT.out"; grep -E '^RACE' "$OUT/driver.log"
grep -E 'cone_follower.*(Traceback|Error)|Autonomous commands lost|FAULT state entered' "$OUT/launch.log" | cut -c1-160 | head -4
python3 - "$OUT" <<'PY'
import csv, sys, numpy as np, math
rows = list(csv.reader(open(sys.argv[1] + '/log.csv')))[1:]
g = np.array([[float(r[0]), float(r[2]), float(r[3]), float(r[4])] for r in rows if r[1] == 'gt'])
mv = np.where(np.hypot(*np.diff(g[:, 1:3], axis=0).T) > 0.005)[0]
if len(mv):
    t0 = g[mv[0], 0]; sp = np.hypot(*np.diff(g[:, 1:3], axis=0).T) / np.maximum(np.diff(g[:, 0]), 1e-3)
    print('drove %.1f s of sim time, %.1f m, top speed %.1f m/s; final pose (%.2f, %.2f, %.0f deg)' % (
        g[-1, 0] - t0, np.sum(np.hypot(*np.diff(g[mv[0]:, 1:3], axis=0).T)), np.percentile(sp[mv[0]:], 99),
        g[-1, 1], g[-1, 2], math.degrees(g[-1, 3])))
PY
grep "last 5 s" "$OUT/launch.log" | grep -oE "rgb [0-9]+|stale control steps [0-9]+" | paste - - |
  awk '{rgb+=$2; st+=$6; n++} END{if (n) printf "camera %.1f fps, stale control steps %.1f%%\n", rgb/n/5, st/n}'
echo "leftover sim processes: $(ps -eo comm | grep -cE 'ruby|state_estimator|cone_follower')"
