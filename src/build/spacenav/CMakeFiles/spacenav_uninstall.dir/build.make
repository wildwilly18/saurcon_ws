# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.28

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/wilson/saurcon_ws/src/joystick_drivers/spacenav

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/wilson/saurcon_ws/src/build/spacenav

# Utility rule file for spacenav_uninstall.

# Include any custom commands dependencies for this target.
include CMakeFiles/spacenav_uninstall.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/spacenav_uninstall.dir/progress.make

CMakeFiles/spacenav_uninstall:
	/usr/bin/cmake -P /home/wilson/saurcon_ws/src/build/spacenav/ament_cmake_uninstall_target/ament_cmake_uninstall_target.cmake

spacenav_uninstall: CMakeFiles/spacenav_uninstall
spacenav_uninstall: CMakeFiles/spacenav_uninstall.dir/build.make
.PHONY : spacenav_uninstall

# Rule to build all files generated by this target.
CMakeFiles/spacenav_uninstall.dir/build: spacenav_uninstall
.PHONY : CMakeFiles/spacenav_uninstall.dir/build

CMakeFiles/spacenav_uninstall.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/spacenav_uninstall.dir/cmake_clean.cmake
.PHONY : CMakeFiles/spacenav_uninstall.dir/clean

CMakeFiles/spacenav_uninstall.dir/depend:
	cd /home/wilson/saurcon_ws/src/build/spacenav && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/wilson/saurcon_ws/src/joystick_drivers/spacenav /home/wilson/saurcon_ws/src/joystick_drivers/spacenav /home/wilson/saurcon_ws/src/build/spacenav /home/wilson/saurcon_ws/src/build/spacenav /home/wilson/saurcon_ws/src/build/spacenav/CMakeFiles/spacenav_uninstall.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : CMakeFiles/spacenav_uninstall.dir/depend

