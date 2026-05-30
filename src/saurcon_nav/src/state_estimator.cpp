#include "state_estimator.hpp"

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
    Eigen::MatrixXd S = ((n_ + lambda_) * P_k_p_).llt().matrixL();

    sigma_pts_.col(0) = X_k_p_;
    for(int i = 0; i < n_; i++){
        sigma_pts_.col(i + 1)     = X_k_p_ + S.col(i);
        sigma_pts_.col(i + 1 + n_) = X_k_p_ - S.col(i);
    }
}

bool StateEstimator::initializeStart(){
    auto meas = localization_buffer.front();
    if(meas.seq == 0) return false;

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
    return aruco_init_counts_ >= localization_survey_count;
}

void StateEstimator::measurementUpdate(){
    return
}

void StateEstimator::predictionUpdate(double dt){
    IMU_t imu_meas = imu_buffer.front();

    // Bias-corrected gyro rate — process input driving Theta
    double omega_psi = imu_meas.w_b(2) - gyro_bias_(2);

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
