#include "state_estimator.hpp"
#include <cstdio>

namespace saurcon_nav
{

StateEstimator::StateEstimator()
{
    imu_buffer.resize(100);
    odom_buffer.resize(100);
    localization_buffer.resize(100);
    state_buffer.resize(100);
}

StateEstimator::~StateEstimator()
{
}

// === State Estimator State Handling ===
void StateEstimator::spin(double dt){
    duringNavState(current_state_, dt);
}

void StateEstimator::reset(){
    current_state_ = SaurconNavState::RESET;
}

void StateEstimator::onNavStateChange(SaurconNavState new_state){
    switch(new_state){
        case SaurconNavState::SURVEY:
            initializeUKF();
            break;
        default:
            break;
    }
    last_state_ = new_state;
}

void StateEstimator::duringNavState(SaurconNavState state, double dt){
    switch(state){

        case SaurconNavState::OFF:
            printf("[StateEstimator] OFF -> STARTUP\n");
            current_state_ = SaurconNavState::STARTUP;
            onNavStateChange(current_state_);
            break;

        case SaurconNavState::STARTUP:
            sensors_ready = initializeSensors();
            initializeIMU();
            if(sensors_ready && gyro_bias_ready){
                printf("[StateEstimator] STARTUP -> SURVEY  (imu_counts=%zu odom_counts=%zu)\n",
                       imu_counts, odom_counts);
                current_state_ = SaurconNavState::SURVEY;
                onNavStateChange(current_state_);
            }
            break;

        case SaurconNavState::SURVEY:
            survey_spin_counts_++;
            if(initializeStart()){
                printf("[StateEstimator] SURVEY -> NAVIGATE  (X=%.2f Y=%.2f Theta=%.2f)\n",
                       X_k_p_(STATE_IDX::X), X_k_p_(STATE_IDX::Y), X_k_p_(STATE_IDX::Theta));
                current_state_ = SaurconNavState::NAVIGATE;
                onNavStateChange(current_state_);
            } else if(survey_spin_counts_ >= survey_timeout_count){
                // No ArUco available — initialize at origin and proceed
                printf("[StateEstimator] SURVEY timeout — no ArUco data, initializing at (0,0,0)\n");
                X_k_p_(STATE_IDX::X)     = 0.0;
                X_k_p_(STATE_IDX::Y)     = 0.0;
                X_k_p_(STATE_IDX::V)     = 0.0;
                X_k_p_(STATE_IDX::Theta) = 0.0;
                P_k_p_(STATE_IDX::X,     STATE_IDX::X)     = x_p0_std_*x_p0_std_;
                P_k_p_(STATE_IDX::Y,     STATE_IDX::Y)     = y_p0_std_*y_p0_std_;
                P_k_p_(STATE_IDX::Theta, STATE_IDX::Theta) = theta_p0_std_*theta_p0_std_;
                P_k_p_(STATE_IDX::V,     STATE_IDX::V)     = v_p0_std_*v_p0_std_;
                current_state_ = SaurconNavState::NAVIGATE;
                onNavStateChange(current_state_);
            }
            break;

        case SaurconNavState::NAVIGATE:
            predictionUpdate(dt);
            measurementUpdate();
            break;

        case SaurconNavState::RESET:
            doReset();
            break;
    }
}

void StateEstimator::doReset(){
    imu_counts           = 0;
    odom_counts          = 0;
    gyro_bias_counts     = 0;
    localization_counts  = 0;
    imu_last_seq         = 0;
    imu_ready            = false;
    odom_ready           = false;
    sensors_ready        = false;
    gyro_bias_ready      = false;
    localization_ready   = false;
    first_loop           = true;
    aruco_last_seq_      = 0;
    aruco_init_counts_   = 0;
    survey_spin_counts_  = 0;
    last_localization_time = 0.0;
    gyro_bias_.setZero();
    gz_readings.clear();
    X_k_p_.setZero();
    X_k_m_.setZero();
    P_k_p_.setZero();
    P_k_m_.setZero();
    sigma_pts_.setZero();
    imu_buffer.clear();
    odom_buffer.clear();
    localization_buffer.clear();
    state_buffer.clear();
    imu_buffer.resize(buffer_size);
    odom_buffer.resize(buffer_size);
    localization_buffer.resize(buffer_size);
    state_buffer.resize(buffer_size);
    last_state_    = SaurconNavState::OFF;
    current_state_ = SaurconNavState::OFF;
}

// === Add measurements to buffer, process if needed ===
void StateEstimator::add_measure(ODOM_t measure){
    measure.seq = odom_counts;

    odom_buffer.push_front(measure);
    if(odom_buffer.size() > buffer_size){
        odom_buffer.pop_back();
    }

    odom_counts++;

    odom_ready = odom_counts > odom_survey_count;
}

void StateEstimator::add_measure(IMU_t measure){
    measure.seq = imu_counts;

    imu_buffer.push_front(measure);
    if(imu_buffer.size() > buffer_size){
        imu_buffer.pop_back();
    }

    imu_counts++;

    imu_ready = imu_counts > imu_survey_count;
}

void StateEstimator::add_measure(Aruco_loc_t measure){
    measure.seq = localization_counts;

    localization_buffer.push_front(measure);
    if(localization_buffer.size() > buffer_size){
        localization_buffer.pop_back();
    }

    localization_counts++;

    localization_ready = localization_counts > localization_survey_count; 
}

void StateEstimator::generateSigmaPoints(){
    // Cholesky decomposition of (n + lambda) * P_k_p_
    Eigen::MatrixXd L = ((n_ + lambda_) * P_k_p_).llt().matrixL();

    sigma_pts_.col(0) = X_k_p_;
    for(int i = 0; i < n_; i++){
        sigma_pts_.col(i + 1)      = X_k_p_ + L.col(i);
        sigma_pts_.col(i + 1 + n_) = X_k_p_ - L.col(i);
    }
}

bool StateEstimator::initializeStart(){
    if(localization_counts == 0) return false;    // no ArUco data yet

    auto meas = localization_buffer.front();

    if(first_loop){
        X_k_p_(STATE_IDX::X)     = meas.x;
        X_k_p_(STATE_IDX::Y)     = meas.y;
        X_k_p_(STATE_IDX::V)     = 0.0;
        X_k_p_(STATE_IDX::Theta) = meas.theta;

        P_k_p_(STATE_IDX::X,     STATE_IDX::X)     = x_p0_std_*x_p0_std_;
        P_k_p_(STATE_IDX::Y,     STATE_IDX::Y)     = y_p0_std_*y_p0_std_;
        P_k_p_(STATE_IDX::Theta, STATE_IDX::Theta) = theta_p0_std_*theta_p0_std_;
        P_k_p_(STATE_IDX::V,     STATE_IDX::V)     = v_p0_std_*v_p0_std_;
        first_loop = false;
    }

    if(meas.seq <= aruco_last_seq_) return false;
    aruco_last_seq_ = meas.seq;

    // Measurement update to refine initial pose estimate
    Eigen::Matrix3d R = Eigen::Matrix3d::Zero();
    R(0,0) = meas.var_x;
    R(1,1) = meas.var_y;
    R(2,2) = meas.var_theta;

    // H is 3×4: selects [X, Y, Theta] from the 4-state vector
    Eigen::Matrix<double, 3, 4> H = Eigen::Matrix<double, 3, 4>::Zero();
    H(0, STATE_IDX::X)     = 1.0;
    H(1, STATE_IDX::Y)     = 1.0;
    H(2, STATE_IDX::Theta) = 1.0;

    // S = H*P*H^T + R  (3×3)
    Eigen::Matrix3d S = H * P_k_p_ * H.transpose() + R;

    // K = P*H^T * S^-1  (4×3)
    Eigen::Matrix<double, 4, 3> K = P_k_p_ * H.transpose() * S.inverse();

    // Innovation with angle wrap on theta
    Eigen::Vector3d innov;
    innov(0) = meas.x - X_k_p_(STATE_IDX::X);
    innov(1) = meas.y - X_k_p_(STATE_IDX::Y);
    innov(2) = std::atan2(std::sin(meas.theta - X_k_p_(STATE_IDX::Theta)),
                           std::cos(meas.theta - X_k_p_(STATE_IDX::Theta)));

    X_k_p_ += K * innov;
    X_k_p_(STATE_IDX::Theta) = std::atan2(std::sin(X_k_p_(STATE_IDX::Theta)),
                                            std::cos(X_k_p_(STATE_IDX::Theta)));

    // Joseph form: (I - K*H)*P*(I - K*H)^T + K*R*K^T
    Eigen::Matrix4d IKH = Eigen::Matrix4d::Identity() - K * H;
    P_k_p_ = IKH * P_k_p_ * IKH.transpose() + K * R * K.transpose();

    aruco_init_counts_++;
    if(aruco_init_counts_ % 10 == 0){
        printf("[StateEstimator] SURVEY progress: %zu / %zu ArUco samples\n",
               aruco_init_counts_, localization_survey_count);
    }
    return aruco_init_counts_ >= localization_survey_count;
}

void StateEstimator::measurementUpdate(){
    auto loc_measure = localization_buffer.front();

    bool fresh_localization = (loc_measure.time_stamp > last_localization_time);

    if(fresh_localization){
        // Setup R matrix
        Eigen::Matrix3d R = Eigen::Matrix3d::Zero();
        
        R(0,0) = loc_measure.var_x;
        R(1,1) = loc_measure.var_y;
        R(2,2) = loc_measure.var_theta;

        // Generate the sigma points
        Eigen::MatrixXd Lm = ((n_ + lambda_) * P_k_m_).llt().matrixL();
        Eigen::MatrixXd sp(n_, 2*n_+1);
        sp.col(0) = X_k_m_;
        for(int i = 0; i<n_; i++){
            sp.col(i+1)    = X_k_m_ + Lm.col(i);
            sp.col(i+1+n_) = X_k_m_ - Lm.col(i);
        }

        // Project sigma points through h(x) = [X,Y,Theta]
        Eigen::MatrixXd z_sp  = sp.topRows<3>(); //3x9
        Eigen::Vector3d z_hat = z_sp * Wm_; // 3x9 X 9x1 = 3x1

        // Innovation Vector
        Eigen::Vector3d innov;
        innov(0) = loc_measure.x - z_hat(0);
        innov(1) = loc_measure.y - z_hat(1);
        innov(2) = std::atan2(std::sin(loc_measure.theta - z_hat(2)),
                        std::cos(loc_measure.theta - z_hat(2)));
        
        // Cenetered measurement sigma points (3x9)
        Eigen::MatrixXd dZ = z_sp.colwise() - z_hat;

        //Angle Wrap the theta row
        for(int i = 0; i<2*n_+1; i++){
            dZ(2,i) = std::atan2(std::sin(dZ(2,i)), std::cos(dZ(2,i)));
        }

        //Sz = dZ * diag(Wc) * dZ^T + R (3x3)
        Eigen::Matrix3d S_z = dZ * Wc_.asDiagonal() * dZ.transpose() + R;

        // Centered State Sigma points (4x9)
        Eigen::MatrixXd dX = sp.colwise() - X_k_m_;

        // Cross-Covariance Pxz = dX * diag(Wc) * dZ^T (4x3)
        Eigen::MatrixXd P_xz = dX * Wc_.asDiagonal() * dZ.transpose();

        // Kalman gain K (4x3)
        Eigen::MatrixXd K = P_xz * S_z.inverse();

        // Apply State Update
        X_k_p_ = X_k_m_ + K * innov;
        X_k_p_(STATE_IDX::Theta) = std::atan2(std::sin(X_k_p_(STATE_IDX::Theta)),
                                                std::cos(X_k_p_(STATE_IDX::Theta)));

        // Apply Covariance Update: P_k_m_ - K * S_z * K^T
        P_k_p_ = P_k_m_ - K * S_z * K.transpose();

        last_localization_time = loc_measure.time_stamp;
    }


    return;
}

void StateEstimator::predictionUpdate(double dt){
    IMU_t imu_meas = imu_buffer.front();

    // Bias-corrected gyro rate — process input driving Theta
    double omega_psi = imu_meas.w_b(2) - gyro_bias_(2);

    // Initialize Q_k_ on this time step
    initializeQ(dt);

    // 1. Generate sigma points from posterior estimate
    generateSigmaPoints();

    // 2. Propagate each sigma point through the CTRV process model
    Eigen::MatrixXd sigma_pts_prop(n_, 2*n_+1);
    for(int i = 0; i < 2*n_+1; i++){
        Eigen::VectorXd s = sigma_pts_.col(i);
        double theta = s(STATE_IDX::Theta);
        double v     = s(STATE_IDX::V);
        double theta_new = theta + omega_psi * dt;

        Eigen::VectorXd s_prop(n_);
        if(std::abs(omega_psi) > 1e-6){
            s_prop(STATE_IDX::X)     = s(STATE_IDX::X) + (v / omega_psi) * (sin(theta_new) - sin(theta));
            s_prop(STATE_IDX::Y)     = s(STATE_IDX::Y) + (v / omega_psi) * (cos(theta)     - cos(theta_new));
        } else {
            s_prop(STATE_IDX::X)     = s(STATE_IDX::X) + v * cos(theta) * dt;
            s_prop(STATE_IDX::Y)     = s(STATE_IDX::Y) + v * sin(theta) * dt;
        }
        s_prop(STATE_IDX::Theta) = theta_new;
        s_prop(STATE_IDX::V)     = v;
        sigma_pts_prop.col(i) = s_prop;
    }

    // 3. Recover predicted mean
    X_k_m_ = sigma_pts_prop * Wm_;

    // 4. Recover predicted covariance and add process noise Q
    P_k_m_.setZero();
    for(int i = 0; i < 2*n_+1; i++){
        Eigen::VectorXd diff = sigma_pts_prop.col(i) - X_k_m_;
        P_k_m_ += Wc_(i) * diff * diff.transpose();
    }
    P_k_m_ += Q_k_;
}

void StateEstimator::initializeQ(double dt){
    Q_k_ = Eigen::Matrix<double, 4,4>::Zero();
    Q_k_(STATE_IDX::Theta, STATE_IDX::Theta) = q_theta_ * dt;
    Q_k_(STATE_IDX::V,     STATE_IDX::V)     = q_v_ * dt;
}

bool StateEstimator::initializeSensors(){
    if(odom_ready && imu_ready){
        return true;
    } else{
        return false;
    }    
}

bool StateEstimator::initializeIMU(){
    if(gyro_bias_counts < imu_survey_count){
        auto imu_reading = imu_buffer.front();

        if(imu_reading.seq > imu_last_seq){
            gz_readings.push_back(imu_reading.w_b);
            gyro_bias_counts++;
            imu_last_seq = imu_reading.seq;
        }

        // Once counter is hit average the bias and store the gyro bias
        if(gyro_bias_counts >= imu_survey_count){
            double x_sum = 0.0, y_sum = 0.0, z_sum = 0.0;

            for(auto& gyro : gz_readings){
                x_sum += gyro(0);
                y_sum += gyro(1);
                z_sum += gyro(2);
            }

            gyro_bias_(0) = x_sum / static_cast<double>(imu_counts);
            gyro_bias_(1) = y_sum / static_cast<double>(imu_counts);
            gyro_bias_(2) = z_sum / static_cast<double>(imu_counts);

            gyro_bias_ready = true;
        }
    }

    return gyro_bias_ready;
}

bool StateEstimator::initializeUKF(){
    // Initialize UKF
    lambda_ = alpha_ * alpha_ * (n_ + kappa_) - n_;
    Wm_(0) = lambda_ / (n_ + lambda_);
    Wc_(0) = Wm_(0) + (1.0 - alpha_*alpha_ + beta_);
    for(int i = 1; i < 2*n_+1; i++){
        Wm_(i) = 1.0 / (2.0 * (n_ + lambda_));
        Wc_(i) = Wm_(i);
    }

    return true;
}

}  // namespace saurcon_nav
