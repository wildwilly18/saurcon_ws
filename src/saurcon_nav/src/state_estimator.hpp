#pragma once

#include <vector>
#include <deque>
#include <Eigen/Dense>

namespace saurcon_nav
{

enum STATE_IDX : int {
    X = 0,
    Y ,
    Theta,
    V,
    SIZE
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

struct Aruco_loc_t{
    double time_stamp = 0.0;
    size_t seq = 0;
    double x     = 0.0;   // world X  (map frame)
    double y     = 0.0;   // world Y  (map frame)
    double theta = 0.0;   // yaw      (map frame, radians)
    double var_x     = 1.0;  // position variance  (m^2)
    double var_y     = 1.0;
    double var_theta = 1.0;  // yaw variance (rad^2)
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
    void add_measure(IMU_t meas);
    void add_measure(ODOM_t meas);
    void add_measure(Aruco_loc_t meas);

    SaurconNavState getCurrentState() const { return current_state_; }

private:
    void onNavStateChange(SaurconNavState new_state);
    void duringNavState(SaurconNavState current_state);

    // Nav Specific functions
    bool initializeSensors();
    bool initializeIMU();
    bool initializeStart();
    bool initializeUKF();

    // Initialize Q matrix each step. 
    void initializeQ();

    // EKF handling calls
    void predictionUpdate(double dt);
    void measurementUpdate();

    // UKF with 4 states [X, Y, Theta, V_body]
    // Gyro (bias-corrected) is the process input driving Theta. Odometry is a measurement of V.
    Eigen::VectorXd X_k_m_ = Eigen::VectorXd::Zero(4);
    Eigen::VectorXd X_k_p_ = Eigen::VectorXd::Zero(4);

    Eigen::MatrixXd P_k_m_ = Eigen::MatrixXd::Zero(4,4);
    Eigen::MatrixXd P_k_p_ = Eigen::MatrixXd::Zero(4,4);

    // Q: X and Y have no direct process noise (deterministic given Theta and V).
    // Theta noise comes from gyro rate uncertainty. V noise from the constant-V model assumption.
    Eigen::MatrixXd Q_k_ = Eigen::MatrixXd::Zero(4,4);
    double gyro_q_std_ = 1E-3;
    double odom_q_std_ = 1E-2;
    double q_theta_{gyro_q_std_ * gyro_q_std_};   // gyro angular rate noise variance (rad/s)^2
    double q_v_{odom_q_std_ * odom_q_std_};        // velocity model noise variance (m/s)^2


    // P: State Initial Probablities
    double x_p0_std_ = 0.2;
    double y_p0_std_ = 0.2;
    double v_p0_std_ = 0.1;
    double theta_p0_std_ = 1E-2;

    // UKF tuning
    const int n_  = 4;
    const double alpha_ = 0.1;
    const double beta_  = 2.0;
    const double kappa_ = 0.0;
    double lambda_; // computed at initialization

    Eigen::VectorXd Wm_ = Eigen::VectorXd::Zero(9);
    Eigen::VectorXd Wc_ = Eigen::VectorXd::Zero(9);

    // Sigma point matrix: each column is one sigma point (n x 2n+1)
    Eigen::MatrixXd sigma_pts_ = Eigen::MatrixXd::Zero(4, 9);

    void generateSigmaPoints();

    // Buffers
    std::deque<IMU_t>                imu_buffer;
    std::deque<ODOM_t>              odom_buffer;
    std::deque<Aruco_loc_t> localization_buffer;

    std::deque<NAV_t> state_buffer;

    SaurconNavState current_state_ = SaurconNavState::OFF;
    SaurconNavState last_state_    = SaurconNavState::OFF;

    Eigen::Vector3d gyro_bias_{0.0, 0.0, 0.0};

    // Startup trackers
    size_t imu_counts{0};
    size_t odom_counts{0};
    size_t gyro_bias_counts{0};
    size_t localization_counts{0};

    size_t buffer_size{100};

    const size_t imu_survey_count = 100;
    const size_t odom_survey_count = 100;
    const size_t localization_survey_count = 100;

    //IMU initialization
    std::vector<Eigen::Vector3d> gz_readings;
    uint16_t imu_last_seq{0};

    bool imu_ready{false};
    bool odom_ready{false};
    bool sensors_ready{false};
    bool gyro_bias_ready{false};
    bool localization_ready{false};

    bool first_loop{true};

    size_t aruco_last_seq_{0};
    size_t aruco_init_counts_{0};
};

}  // namespace saurcon_nav
