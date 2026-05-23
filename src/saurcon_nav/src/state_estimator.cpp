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

// Add measurements to buffer, process if needed

void StateEstimator::spin(double dt){
}

void StateEstimator::predictionUpdate(){
    // Based of Groves Inertial Navigation but applied to 2 dimension(X,Y,Psi)
    // 1. Attitude update. update psi based on the gyro reading.
    IMU_t imu_meas = imu_buffer.front();
    ODOM_t odom_meas = odom_buffer.front();

    double omega_psi = imu_meas.w_b(2) - gyro_bias_;
}

void StateEstimator::init_G(double dt){
    double Theta = X_k_p_(STATE_IDX::Theta);

    G_k_(0,1) = cos(Theta) * dt; // x from v
    G_k_(1,1) = sin(Theta) * dt; // y from v
    G_k_(2,0) = dt;              // theta from omega
}

void StateEstimator::initializeSensors(){
    auto imu_reading = imu_buffer.front();
    auto odom_reading = odom_buffer.front();

    
}

void StateEstimator::initializeIMU(){
    if(gyro_bias_counts < imu_survey_count){
        auto imu_reading = imu_buffer.front();

        if(imu_reading.seq > imu_last_seq){
            gz_readings.push_back(imu_reading.w_b);
            gyro_bias_counts;
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
}

}  // namespace saurcon_nav
