# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_wiimote_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED wiimote_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(wiimote_FOUND FALSE)
  elseif(NOT wiimote_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(wiimote_FOUND FALSE)
  endif()
  return()
endif()
set(_wiimote_CONFIG_INCLUDED TRUE)

# output package information
if(NOT wiimote_FIND_QUIETLY)
  message(STATUS "Found wiimote: 3.3.0 (${wiimote_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'wiimote' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT wiimote_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(wiimote_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "wiimote-extras.cmake;ament_cmake_export_targets-extras.cmake;ament_cmake_export_dependencies-extras.cmake")
foreach(_extra ${_extras})
  include("${wiimote_DIR}/${_extra}")
endforeach()
