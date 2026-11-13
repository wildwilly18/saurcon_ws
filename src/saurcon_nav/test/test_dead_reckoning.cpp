#include "state_estimator.hpp"
#include <cmath>
#include <stdexcept>
using namespace saurcon_nav;
void check(bool ok) { if (!ok) throw std::runtime_error("dead reckoning regression"); }
void sample(StateEstimator& e, double v=0, double w=0) {
    IMU_t imu; imu.w_b(2)=w; e.add_measure(imu);
    ODOM_t odom; odom.v_b=v; e.add_measure(odom); e.spin(.02);
}
int main() {
    StateEstimator e(false), original;
    for (int i=0;i<110;++i) {sample(e);sample(original);}
    check(e.getCurrentState()==SaurconNavState::NAVIGATE);
    check(original.getCurrentState()==SaurconNavState::SURVEY);
    check(e.getX().norm()<1e-8);
    double variance=e.getP()(0,0);
    for (int i=0;i<50;++i) sample(e,1);
    check(std::abs(e.getX()(0)-1)<.001);
    check(e.getP()(0,0)>variance);
    Aruco_loc_t fix;fix.x=100;fix.y=100;e.add_measure(fix);sample(e);
    check(e.getX()(0)<1.01);
    for(int i=0;i<50;++i)sample(e,1,1);
    check(std::abs(e.getX()(2)-1)<.001);
    check(std::abs(e.getYawRate()-1)<1e-9);
    check(std::abs(e.getX()(0)-(1+std::sin(1)))<.002);
    check(std::abs(e.getX()(1)-(1-std::cos(1)))<.002);
    check(e.getP().allFinite());
    e.reset();sample(e);for(int i=0;i<110;++i)sample(e);
    check(e.getCurrentState()==SaurconNavState::NAVIGATE);
    check(e.getX().norm()<1e-8);

    // Gyro bias refinement while stopped. True bias 0.010 rad/s; the 1 s start-up
    // calibration sees noisy samples averaging 0.012 rad/s (a 20% error).
    StateEstimator b(false);
    for (int i=0;i<110;++i) sample(b,0,(i%2==0)?0.024:0.0);
    check(b.getCurrentState()==SaurconNavState::NAVIGATE);
    for (int i=0;i<3000;++i) sample(b,0,0.010);          // parked: refine
    for (int i=0;i<500;++i) sample(b,1,0.010);            // drive straight 10 s
    check(std::abs(b.getX()(2))<0.002);                   // heading barely drifts
    check(std::abs(b.getX()(1))<0.01);

    // A knock while parked (above the gate) must not corrupt the estimate.
    StateEstimator k(false);
    for (int i=0;i<110;++i) sample(k,0,0.010);
    for (int i=0;i<50;++i) sample(k,0,1.0);               // rotates heading, rejected for bias
    const double heading_after_knock = k.getX()(2);
    for (int i=0;i<500;++i) sample(k,1,0.010);
    check(std::abs(k.getX()(2)-heading_after_knock)<0.002);
}
