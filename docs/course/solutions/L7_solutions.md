# Lecture 7 — Solutions

### 7.1 [C] Two alignments

**Method.** Score one mapping run with `analyze.py --align` (first shared pose) and with a
least-squares SE(2) fit (Umeyama with scale fixed to 1) over the whole trajectory.

**Expected result.** The least-squares ATE is always ≤ the first-pose ATE, often by a factor of 2 or
more on a drifting run, because the fit absorbs initial offset and the average drift into the
transform. The two answer different questions: first-pose alignment measures **how well the system
localizes from where it started**, which a controller experiences; best-fit measures **the shape** of
the trajectory, which is useful for comparing maps from different frames. Report the first; report the
second only with that caveat.

### 7.2 [T] Rule of three

See the lecture's answer. Note the one-sided/two-sided distinction: the one-sided 95% bound uses
$0.05^{1/n}$ (rule of three, $3/n$); the two-sided Clopper–Pearson limit in (7.1) uses $0.025^{1/n}$
(about $3.7/n$). Either is accepted if stated.

### 7.3 [C] Five seeds of the marker-free UKF run

**Method.** Five runs with different `ROS_DOMAIN_ID`/seed, identical everything else; ATE with
first-pose alignment; report $\bar x \pm t_{0.975,4}\,s/\sqrt5$ with $t_{0.975,4} = 2.776$.

**Expected result.** A mean near the single-run 0.070 m, with an interval of a few centimetres. The
single-run claim is "supported" if 0.070 lies inside the interval, but the right conclusion states
the interval, not the point. Penalise answers that report the best seed.

### 7.4 [T] Paired runs for a 0.3 s improvement

See the lecture's answer: about 14 pairs (≈ 16 with the $t$ correction). Full credit discusses
pairing: an unpaired design with per-run standard deviation $\sigma_\text{run}$ needs
$2(\sigma_\text{run}/\sigma_\text{diff})^2$ times as many runs, which is large when runs share
variance (the same track and start).

### 7.5 [C] Detect a stray simulator

```bash
# in runsim.sh, before the launch:
stray=$(ps -eo pid=,comm= | awk '$2 == "ruby" || $2 == "gz" {print $1}')
if [ -n "$stray" ]; then
  echo "refusing to start: Gazebo already running (pids: $stray)" >&2; exit 1
fi
# ... and 8 s after the launch:
n=$(ps -eo comm= | grep -cxE 'ruby|gz')
[ "$n" -le 1 ] || { echo "more than one Gazebo process ($n)" >&2; exit 1; }
```

Match on the **process name** (`comm`), exactly, never on the command line: `pgrep -f gz` matches the
shell running the check itself, which is the bug of §3. Rubric: correct detection (4), no
self-matching (3), placement before and after launch (3).
