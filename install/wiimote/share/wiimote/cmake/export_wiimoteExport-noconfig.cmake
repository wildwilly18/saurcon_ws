#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "wiimote::wiimote_lib" for configuration ""
set_property(TARGET wiimote::wiimote_lib APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(wiimote::wiimote_lib PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libwiimote_lib.so"
  IMPORTED_SONAME_NOCONFIG "libwiimote_lib.so"
  )

list(APPEND _cmake_import_check_targets wiimote::wiimote_lib )
list(APPEND _cmake_import_check_files_for_wiimote::wiimote_lib "${_IMPORT_PREFIX}/lib/libwiimote_lib.so" )

# Import target "wiimote::teleop_wiimote" for configuration ""
set_property(TARGET wiimote::teleop_wiimote APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(wiimote::teleop_wiimote PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libteleop_wiimote.so"
  IMPORTED_SONAME_NOCONFIG "libteleop_wiimote.so"
  )

list(APPEND _cmake_import_check_targets wiimote::teleop_wiimote )
list(APPEND _cmake_import_check_files_for_wiimote::teleop_wiimote "${_IMPORT_PREFIX}/lib/libteleop_wiimote.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
