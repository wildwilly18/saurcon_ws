#pragma once

#include <vector>
#include <Eigen/Dense>

namespace saurcon_nav
{

enum class SaurconNavState : int {
    OFF = 0,
    STARTUP,
    SURVEY,
    NAVIGATE
};

struct IMU_t{
    Eigen::Vector3d accel;
    Eigen::Vector3d w_b;
};

struct ODOM_t{
    Eigen::Vector3d v_b;
};

class StateEstimator
{
public:
    StateEstimator();
    ~StateEstimator();

    void resetStateEstimator();

    SaurconNavState getCurrentState() const { return current_state_; }

private:
    void onStateChange(SaurconNavState new_state);
    void duringState(SaurconNavState current_state);


    SaurconNavState current_state_;
};

}  // namespace saurcon_nav
