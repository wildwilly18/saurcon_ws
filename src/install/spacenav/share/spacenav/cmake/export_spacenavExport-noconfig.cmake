#----------------------------------------------------------------
# Generated CMake target import file.
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "spacenav::spacenav" for configuration ""
set_property(TARGET spacenav::spacenav APPEND PROPERTY IMPORTED_CONFIGURATIONS NOCONFIG)
set_target_properties(spacenav::spacenav PROPERTIES
  IMPORTED_LOCATION_NOCONFIG "${_IMPORT_PREFIX}/lib/libspacenav.so"
  IMPORTED_SONAME_NOCONFIG "libspacenav.so"
  )

list(APPEND _cmake_import_check_targets spacenav::spacenav )
list(APPEND _cmake_import_check_files_for_spacenav::spacenav "${_IMPORT_PREFIX}/lib/libspacenav.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
