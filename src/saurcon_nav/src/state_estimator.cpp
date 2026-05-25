#include "state_estimator.hpp"

namespace saurcon_nav
{

StateEstimator::StateEstimator()
{
    imu_buffer.resize(100);
    odom_buffer.resize(100);
}

StateEstimator::~StateEstimator()
{
}

// === State Estimator State Handling ===

// === Add measurements to buffer, process if needed ===
void StateEstimator::add_measure(ODOM_t measure){
    measure.seq = odom_counts;

    odom_buffer.push_front(measure);
    odom_buffer.pop_back();

    odom_counts++;

    odom_ready = odom_counts > odom_survey_count;
}

void StateEstimator::add_measure(IMU_t measure){
    measure.seq = imu_counts;

    imu_buffer.push_front(measure);
    imu_buffer.pop_back();

    imu_counts++;

    imu_ready = imu_counts > imu_survey_count;
}


void StateEstimator::spin(double dt){
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
