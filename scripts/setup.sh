#!/usr/bin/env bash
# One-time setup for the SAURCON workspace on Ubuntu 24.04 (ROS 2 Jazzy + Gazebo Harmonic).
# Usage: ./scripts/setup.sh     (asks for sudo to install apt packages)
set -euo pipefail

WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_DISTRO=jazzy

. /etc/os-release
if [ "${VERSION_CODENAME:-}" != "noble" ]; then
  echo "This script targets Ubuntu 24.04 (noble); found ${PRETTY_NAME:-unknown}." >&2
  exit 1
fi

echo "==> Adding the ROS 2 apt repository"
sudo apt-get update
sudo apt-get install -y software-properties-common curl git
sudo add-apt-repository -y universe
if ! dpkg -s ros2-apt-source >/dev/null 2>&1; then
  ver=$(curl -fsSL https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
        | grep -F '"tag_name"' | awk -F'"' '{print $4}')
  deb=$(mktemp --suffix=.deb)
  curl -fsSL -o "$deb" \
    "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ver}/ros2-apt-source_${ver}.${VERSION_CODENAME}_all.deb"
  sudo apt-get install -y "$deb"
  rm -f "$deb"
fi

echo "==> Installing ROS 2 ${ROS_DISTRO}, build tools and Gazebo"
sudo apt-get update
sudo apt-get install -y \
  build-essential cmake \
  ros-${ROS_DISTRO}-desktop ros-dev-tools \
  ros-${ROS_DISTRO}-ros-gz

echo "==> Fetching submodules (micro-ROS agent)"
git -C "$WS_DIR" submodule update --init --recursive

echo "==> Installing package dependencies with rosdep"
[ -f /etc/ros/rosdep/sources.list.d/20-default.list ] || sudo rosdep init
rosdep update --rosdistro ${ROS_DISTRO}
set +u; source /opt/ros/${ROS_DISTRO}/setup.bash; set -u
# Resolve first, then install in one apt call (a single sudo prompt).
rosdep_pkgs=$(rosdep install --from-paths "$WS_DIR/src" --ignore-src -r --simulate \
                --rosdistro ${ROS_DISTRO} | awk '/apt-get install/ {print $NF}' | sort -u)
if [ -n "$rosdep_pkgs" ]; then
  # shellcheck disable=SC2086
  sudo apt-get install -y $rosdep_pkgs
fi

echo "==> Joystick access (joy_node)"
if ! id -nG "$USER" | grep -qw input; then
  sudo usermod -aG input "$USER"
  echo "    Added $USER to the 'input' group - log out and back in for it to apply."
fi

echo "==> Building the workspace"
cd "$WS_DIR"
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

cat <<MSG

Setup complete. In each new terminal:
  source /opt/ros/${ROS_DISTRO}/setup.bash
  source $WS_DIR/install/setup.bash

Then, for the full simulation:
  ros2 launch saurcon_rc full_sim_saurcon.launch.py
MSG
