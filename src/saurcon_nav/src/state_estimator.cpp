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

void StateEstimator::spin(double dt){
}

void StateEstimator::init_G(double dt){
    double Theta = X_k_p_(STATE_IDX::Theta);

    G_k_(0,1) = cos(Theta) * dt; // x from v
    G_k_(1,1) = sin(Theta) * dt; // y from v
    G_k_(2,0) = dt;              // theta from omega
}

}  // namespace saurcon_nav
