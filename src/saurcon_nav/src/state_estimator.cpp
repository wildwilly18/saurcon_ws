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

}  // namespace saurcon_nav
