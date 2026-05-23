#pragma once

#include <vector>
#include <deque>
#include <Eigen/Dense>

namespace saurcon_nav
{

enum STATE_IDX : int {
    X = 0,
    Y ,
    Theta
};

enum class SaurconNavState : int {
    OFF = 0,
    STARTUP,
    SURVEY,
    NAVIGATE
};

struct NAV_t{
    double time_stamp = 0.0;
    double X = 0;
    double Y = 0;
    double Theta = 0;
    double V = 0;
    double X_P = 1;
    double Y_P = 1;
    double Theta_P = 0.1;
    double V_P = 0.2;
};

struct IMU_t{
    double time_stamp = 0.0;
    size_t seq = 0;
    Eigen::Vector3d accel = Eigen::Vector3d::Zero();
    Eigen::Vector3d w_b = Eigen::Vector3d::Zero();
};

struct ODOM_t{
    double time_stamp = 0.0;
    size_t seq = 0;
    double v_b = 0.0;
};

class StateEstimator
{
public:
    StateEstimator();
    ~StateEstimator();

    // reset interface call
    void reset();

    // EKF interface
    void spin(double dt);

    // buffer helpers process as needed.
    void add_imu_measure();

    void add_odom_measure();
    void add_aruco_measure();

    void add_aruco_measure();

    SaurconNavState getCurrentState() const { return current_state_; }

private:
    void onNavStateChange(SaurconNavState new_state);
    void duringNavState(SaurconNavState current_state);

    // Nav Specific functions
    void initializeSensors();
    void initializeIMU();
    void initializeEKF();

    // Initialize Q matrix each step. 
    void initializeQ();

    // EKF handling calls
    void predictionUpdate();
    void measurementUpdate();

    // For this EKF we will be using a simple 4 state EKF with states [X Y Theta V_body]
    // The EKF inputs are velocity in body x from wheel odometry and gyro_z bias corrected values.
    Eigen::VectorXd X_k_m_ = Eigen::VectorXd::Zero(4);
    Eigen::VectorXd X_k_p_ = Eigen::VectorXd::Zero(4);

    Eigen::MatrixXd P_k_m_ = Eigen::MatrixXd::Zero(4,4);
    Eigen::MatrixXd P_k_p_ = Eigen::MatrixXd::Zero(4,4);

    Eigen::MatrixXd Q_k_ = Eigen::MatrixXd::Identity(4,4);

    Eigen::MatrixXd G_k_ = Eigen::MatrixXd::Zero(4,2);

    void init_G(double dt);

    // Buffers
    std::deque<IMU_t>   imu_buffer;
    std::deque<ODOM_t> odom_buffer;

    std::deque<NAV_t> state_buffer;

    SaurconNavState current_state_ = SaurconNavState::OFF;
    SaurconNavState last_state_    = SaurconNavState::OFF;

    Eigen::Vector3d gyro_bias_{0.0, 0.0, 0.0};

    // Startup trackers
    size_t imu_counts{0};
    size_t odom_counts{0};
    size_t gyro_bias_counts{0};
    size_t localization_counts{0};

    const size_t imu_survey_count = 100;
    const size_t odom_survey_count = 100;
    const size_t localization_survey_count = 100;

    //IMU initialization
    std::vector<Eigen::Vector3d> gz_readings;
    uint16_t imu_last_seq{0.0};

    bool imu_ready{false};
    bool odom_ready{false};
    bool sensors_ready{false};
    bool gyro_bias_ready{false};
    bool localization_ready{false};
};

}  // namespace saurcon_nav
