#pragma once
#include <cstdint>

enum class SaurconState : uint8_t{
    NO_STATE = 0,      // Initial or invalid state
    STARTUP,          // Startup push to standby to wait for esp32
    STANDBY,          // Startup completed, waiting to control esp32
    RUN_CONTROL,      // Operation via controller
    RUN_AUTONOMOUS,   // Operation via raspi
    FAULT             // General fault state
};

// These are used to track the state of the esp32 managed states. Better naming maybe?
enum class SaurconRCState: uint8_t{
    NO_STATE = 0,     // Initial or invalid state
    STARTUP,          // Power-on init
    STARTUP_ROS,          // ROS2 initialization
    SETUP,            // Motor and encoder setup
    STANDBY,          // Startup complete wait for action
    RUN_CONTROL,      // Operation via controller
    RUN_AUTONOMOUS,   // Operation via raspi
    FAULT,            // General fault state
    FAULT_ROS         // ROS-specific fault
};