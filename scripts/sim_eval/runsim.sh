#!/usr/bin/env bash
# runsim.sh [workspace] [new-output-directory] [launch arguments...]
set -eo pipefail
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="${1:-$(cd "$D/../.." && pwd)}"
OUT="${2:-$WS/evaluation/$(date +%Y%m%d_%H%M%S)}"
if (( $# >= 2 )); then shift 2; else set --; fi
mkdir -p "$(dirname "$OUT")"
mkdir "$OUT" # refuse to overwrite previous measurements
OUT="$(cd "$OUT" && pwd)"
exec 9>"$WS/.sim_eval.lock"
flock -n 9 || { echo "Another evaluation is running" >&2; exit 1; }
source /opt/ros/jazzy/setup.bash
source "$WS/install/setup.bash"
export SAURCON_WS="$WS"
export GZ_PARTITION="saurcon_eval_$$"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-42}"
for a in "$@"; do case "$a" in world:=*) export SIM_WORLD="${a#world:=}";; esac; done
export SIM_WORLD="${SIM_WORLD:-$WS/src/middle_earth/worlds/racetrack.world}"
printf "ROS_DOMAIN_ID=%s\nGZ_PARTITION=%s\nSIM_WORLD=%s\n" "$ROS_DOMAIN_ID" "$GZ_PARTITION" "$SIM_WORLD" > "$OUT/environment.txt"
pids=()
cleanup() {
  trap - EXIT INT TERM
  for pid in "${pids[@]}"; do kill -INT -- "-$pid" 2>/dev/null || true; done
  sleep 5
  for pid in "${pids[@]}"; do kill -TERM -- "-$pid" 2>/dev/null || true; done
  sleep 2
  for pid in "${pids[@]}"; do kill -KILL -- "-$pid" 2>/dev/null || true; done
  wait || true
}
trap cleanup EXIT INT TERM
setsid ros2 launch saurcon_rc full_sim_saurcon.launch.py headless:=true record:=false "$@" > "$OUT/launch.log" 2>&1 9>&- &
pids+=("$!")
sleep 8
kill -0 "${pids[0]}" || { echo "Simulation launch failed; see $OUT/launch.log" >&2; exit 1; }
setsid python3 "$D/gt_bridge.py" > "$OUT/gt_bridge.log" 2>&1 9>&- &
pids+=("$!")
setsid python3 "$D/logger.py" "$OUT" > "$OUT/logger.log" 2>&1 9>&- &
pids+=("$!")
setsid python3 "$D/capture_map.py" "$OUT" > "$OUT/map_capture.log" 2>&1 9>&- &
pids+=("$!")
if [ "${CHASE:-0}" = "1" ]; then   # chase-camera video frames (renders only while subscribed)
  setsid python3 "$D/gz_camera_recorder.py" /chase/image "$OUT/chase" > "$OUT/chase.log" 2>&1 9>&- &
  pids+=("$!")
fi
setsid python3 "$D/${DRIVER:-driver.py}" 20 > "$OUT/driver.log" 2>&1 9>&- &
pids+=("$!")
wait "${pids[-1]}"
echo "Run saved to $OUT"
