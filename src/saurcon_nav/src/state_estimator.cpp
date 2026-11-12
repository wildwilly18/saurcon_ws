#include "state_estimator.hpp"
#include <cstdio>
#include <cmath>
#include <algorithm>

namespace saurcon_nav
{

StateEstimator::StateEstimator(bool use_aruco) : use_aruco_(use_aruco)
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
            if (!use_aruco_) {
                initializePose(0.0, 0.0, 0.0, 0.001, 0.001);
                imu_consumed_ = imu_counts;
                current_state_ = SaurconNavState::NAVIGATE;
                onNavStateChange(current_state_);
                break;
            }
            survey_spin_counts_++;
            if(initializeStart()){
                printf("[StateEstimator] SURVEY -> NAVIGATE  (X=%.2f Y=%.2f Theta=%.2f)\n",
                       X_k_p_(STATE_IDX::X), X_k_p_(STATE_IDX::Y), X_k_p_(STATE_IDX::Theta));
                current_state_ = SaurconNavState::NAVIGATE;
                onNavStateChange(current_state_);
            } else if(survey_spin_counts_ >= survey_timeout_count){
                // No ArUco available — initialize at origin and proceed
                // The pose is unknown, so start with a wide covariance: the first ArUco
                // fix that does arrive must pass the innovation gate and dominate.
                printf("[StateEstimator] SURVEY timeout — no ArUco data, initializing at (0,0,0) with unknown pose\n");
                initializePose(0.0, 0.0, 0.0, unknown_xy_std_, unknown_theta_std_);
                loc_consumed_ = localization_counts;
                current_state_ = SaurconNavState::NAVIGATE;
                onNavStateChange(current_state_);
            }
            break;

        case SaurconNavState::NAVIGATE: {
            // If the vehicle is neither translating nor rotating, bypass prediction
            // and noise injection and carry state/covariance forward unchanged.
            const double v_now     = odom_buffer.empty() ? 0.0 : odom_buffer.front().v_b;
            const double omega_now = imu_buffer.empty()  ? 0.0
                                     : imu_buffer.front().w_b(2) - gyro_bias_(2);
            const bool wheels_still = std::abs(v_now) < stationary_speed_;
            const bool stationary = wheels_still &&
                                    std::abs(omega_now) < stationary_yawrate_;
            if (wheels_still) {
                refineGyroBias();
            }
            if (stationary || dt <= 0.0) {
                imu_consumed_ = imu_counts;   // do not integrate these samples later
                predictionUpdateBypass();
            } else {
                predictionUpdate(dt);
            }
            measurementUpdate();

            if (!stateIsFinite()) {
                printf("[StateEstimator] state is not finite — resetting estimator\n");
                current_state_ = SaurconNavState::RESET;
            }
            break;
        }

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
    imu_consumed_        = 0;
    loc_consumed_        = 0;
    consecutive_rejects_ = 0;
    aruco_init_counts_   = 0;
    survey_spin_counts_  = 0;
    gyro_bias_.setZero();
    bias_samples_        = 0;
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
    if (!use_aruco_) return;
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
    Eigen::MatrixXd L;
    sigmaRoot(P_k_p_, L);

    sigma_pts_.col(0) = X_k_p_;
    for(int i = 0; i < n_; i++){
        sigma_pts_.col(i + 1)      = X_k_p_ + L.col(i);
        sigma_pts_.col(i + 1 + n_) = X_k_p_ - L.col(i);
    }
}

bool StateEstimator::initializeStart(){
    if(loc_consumed_ >= localization_counts) return false;    // nothing new

    // Use the newest fix; mark everything up to it as consumed so NAVIGATE does
    // not apply the same measurement again.
    auto meas = localization_buffer.front();
    loc_consumed_ = localization_counts;

    if(first_loop){
        initializePose(meas.x, meas.y, meas.theta, x_p0_std_, theta_p0_std_);
        P_k_p_(STATE_IDX::Y, STATE_IDX::Y) = y_p0_std_*y_p0_std_;
        first_loop = false;
    }

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
    conditionCovariance(P_k_p_);

    aruco_init_counts_++;
    if(aruco_init_counts_ % 10 == 0){
        printf("[StateEstimator] SURVEY progress: %zu / %zu ArUco samples\n",
               aruco_init_counts_, localization_survey_count);
    }
    return aruco_init_counts_ >= localization_survey_count;
}

void StateEstimator::measurementUpdate(){
    // Default behavior: if no fresh measurement arrives this cycle,
    // carry the prediction straight through to posterior.
    X_k_p_ = X_k_m_;
    P_k_p_ = P_k_m_;
    X_k_p_(STATE_IDX::Theta) = std::atan2(std::sin(X_k_p_(STATE_IDX::Theta)),
                                          std::cos(X_k_p_(STATE_IDX::Theta)));

    // Apply every localization fix that arrived since the last cycle, oldest first.
    // Several markers seen in one camera frame produce several fixes with the same
    // timestamp, so freshness is tracked by arrival count rather than by time.
    size_t pending = localization_counts - loc_consumed_;
    pending = std::min(pending, localization_buffer.size());
    for(size_t i = pending; i-- > 0; ){
        applyLocalization(localization_buffer[i]);
    }
    loc_consumed_ = localization_counts;
}

// One UKF measurement update of the posterior (X_k_p_, P_k_p_) with h(x) = [X, Y, Theta].
void StateEstimator::applyLocalization(const Aruco_loc_t& loc_measure){
    constexpr double kMahalanobisSigmaGate = 5.0;
    constexpr double kMahalanobisD2Gate = kMahalanobisSigmaGate * kMahalanobisSigmaGate;

    const Eigen::VectorXd X_prior = X_k_p_;
    const Eigen::MatrixXd P_prior = P_k_p_;

    // Setup R matrix
    Eigen::Matrix3d R = Eigen::Matrix3d::Zero();
    R(0,0) = loc_measure.var_x;
    R(1,1) = loc_measure.var_y;
    R(2,2) = loc_measure.var_theta;

    // Generate the sigma points
    Eigen::MatrixXd Lm;
    sigmaRoot(P_prior, Lm);
    Eigen::MatrixXd sp(n_, 2*n_+1);
    sp.col(0) = X_prior;
    for(int i = 0; i<n_; i++){
        sp.col(i+1)    = X_prior + Lm.col(i);
        sp.col(i+1+n_) = X_prior - Lm.col(i);
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

    // Mahalanobis innovation gating (5-sigma threshold)
    // d^2 = innov^T * S_z^-1 * innov
    const double maha_d2 = (innov.transpose() * S_z.inverse() * innov)(0,0);
    if(!std::isfinite(maha_d2) || maha_d2 > kMahalanobisD2Gate){
        // Reject outlier localization update; keep the prior as posterior.
        consecutive_rejects_++;
        if(consecutive_rejects_ >= max_consecutive_rejects_){
            // The filter has diverged from what the markers keep reporting.
            // Trust the markers and start again from this fix.
            printf("[StateEstimator] %zu consecutive ArUco fixes rejected — re-initialising pose "
                   "(X=%.2f Y=%.2f Theta=%.2f)\n",
                   consecutive_rejects_, loc_measure.x, loc_measure.y, loc_measure.theta);
            const double v = X_k_p_(STATE_IDX::V);
            initializePose(loc_measure.x, loc_measure.y, loc_measure.theta,
                           x_p0_std_, theta_p0_std_);
            X_k_p_(STATE_IDX::V) = std::isfinite(v) ? v : 0.0;
            consecutive_rejects_ = 0;
        }
        return;
    }
    consecutive_rejects_ = 0;

    // Centered State Sigma points (4x9)
    Eigen::MatrixXd dX = sp.colwise() - X_prior;

    // Cross-Covariance Pxz = dX * diag(Wc) * dZ^T (4x3)
    Eigen::MatrixXd P_xz = dX * Wc_.asDiagonal() * dZ.transpose();

    // Kalman gain K (4x3)
    Eigen::MatrixXd K = P_xz * S_z.inverse();

    // Apply State Update
    X_k_p_ = X_prior + K * innov;
    X_k_p_(STATE_IDX::Theta) = std::atan2(std::sin(X_k_p_(STATE_IDX::Theta)),
                                            std::cos(X_k_p_(STATE_IDX::Theta)));

    // Apply Covariance Update: P - K * S_z * K^T
    P_k_p_ = P_prior - K * S_z * K.transpose();
    conditionCovariance(P_k_p_);
}

void StateEstimator::initializePose(double x, double y, double theta,
                                    double xy_std, double theta_std){
    X_k_p_.setZero();
    X_k_p_(STATE_IDX::X)     = x;
    X_k_p_(STATE_IDX::Y)     = y;
    X_k_p_(STATE_IDX::Theta) = theta;
    X_k_p_(STATE_IDX::V)     = 0.0;

    P_k_p_.setZero();
    P_k_p_(STATE_IDX::X,     STATE_IDX::X)     = xy_std*xy_std;
    P_k_p_(STATE_IDX::Y,     STATE_IDX::Y)     = xy_std*xy_std;
    P_k_p_(STATE_IDX::Theta, STATE_IDX::Theta) = theta_std*theta_std;
    P_k_p_(STATE_IDX::V,     STATE_IDX::V)     = v_p0_std_*v_p0_std_;

    X_k_m_ = X_k_p_;
    P_k_m_ = P_k_p_;
}

// Keep a covariance symmetric with a strictly positive diagonal.
void StateEstimator::conditionCovariance(Eigen::MatrixXd& P){
    constexpr double kMinVariance = 1e-9;
    P = 0.5 * (P + P.transpose()).eval();
    for(int i = 0; i < P.rows(); i++){
        if(!(P(i,i) > kMinVariance)) P(i,i) = kMinVariance;
    }
}

// Lower Cholesky factor of (n + lambda) * P. If P is not positive definite, inflate the
// diagonal until it is; as a last resort fall back to the diagonal of P.
bool StateEstimator::sigmaRoot(const Eigen::MatrixXd& P, Eigen::MatrixXd& L){
    Eigen::MatrixXd Pc = P;
    conditionCovariance(Pc);
    double jitter = 0.0;
    for(int attempt = 0; attempt < 6; attempt++){
        Eigen::MatrixXd scaled = (n_ + lambda_) * Pc;
        scaled.diagonal().array() += jitter;
        Eigen::LLT<Eigen::MatrixXd> llt(scaled);
        if(llt.info() == Eigen::Success){
            L = llt.matrixL();
            return true;
        }
        jitter = (jitter == 0.0) ? 1e-9 : jitter * 100.0;
    }
    L = ((n_ + lambda_) * Pc.diagonal()).cwiseSqrt().asDiagonal();
    return false;
}

bool StateEstimator::stateIsFinite() const {
    return X_k_p_.allFinite() && P_k_p_.allFinite();
}

// Fold the IMU samples received since the last cycle into the gyro bias estimate.
// Called only while the wheels are stopped. Does not consume the samples.
void StateEstimator::refineGyroBias(){
    if(!gyro_bias_ready) return;
    size_t pending = imu_counts - imu_consumed_;
    pending = std::min(pending, imu_buffer.size());
    for(size_t i = pending; i-- > 0; ){
        const Eigen::Vector3d& w = imu_buffer[i].w_b;
        if((w - gyro_bias_).cwiseAbs().maxCoeff() > bias_gate_) continue;
        bias_samples_ = std::min(bias_samples_ + 1, max_bias_samples_);
        gyro_bias_ += (w - gyro_bias_) / static_cast<double>(bias_samples_);
    }
}

// Mean bias-corrected yaw rate over the IMU samples received since the last
// prediction step, so no sample is dropped when the IMU is faster than the filter.
double StateEstimator::meanGyroZ(){
    size_t pending = imu_counts - imu_consumed_;
    pending = std::min(pending, imu_buffer.size());
    imu_consumed_ = imu_counts;
    if(pending == 0){
        return imu_buffer.empty() ? 0.0 : imu_buffer.front().w_b(2) - gyro_bias_(2);
    }
    double sum = 0.0;
    for(size_t i = 0; i < pending; i++){
        sum += imu_buffer[i].w_b(2);
    }
    return sum / static_cast<double>(pending) - gyro_bias_(2);
}

void StateEstimator::predictionUpdate(double dt){
    // Bias-corrected gyro rate — process input driving Theta
    double omega_psi = meanGyroZ();
    
    // Use latest odometry forward velocity as control input for dead reckoning.
    // If odometry is unavailable, fall back to current state velocity.
    double v_ctrl = X_k_p_(STATE_IDX::V);
    if (!odom_buffer.empty()) {
        v_ctrl = odom_buffer.front().v_b;
    }

    // Initialize Q_k_ on this time step
    initializeQ(dt);
    const double q_xy_std = q_xy_base_std_ + q_xy_speed_std_ * std::abs(v_ctrl);
    Q_k_(STATE_IDX::X, STATE_IDX::X) = q_xy_std * q_xy_std * dt;
    Q_k_(STATE_IDX::Y, STATE_IDX::Y) = q_xy_std * q_xy_std * dt;

    // 1. Generate sigma points from posterior estimate
    generateSigmaPoints();

    // 2. Propagate each sigma point through the CTRV process model
    Eigen::MatrixXd sigma_pts_prop(n_, 2*n_+1);
    for(int i = 0; i < 2*n_+1; i++){
        Eigen::VectorXd s = sigma_pts_.col(i);
        double theta = s(STATE_IDX::Theta);
        double v     = v_ctrl;
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
        s_prop(STATE_IDX::V)     = v_ctrl;
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
    conditionCovariance(P_k_m_);
}

void StateEstimator::predictionUpdateBypass(){
    X_k_m_ = X_k_p_;
    P_k_m_ = P_k_p_;

    // Keep heading wrapped even during bypass cycles.
    X_k_m_(STATE_IDX::Theta) = std::atan2(std::sin(X_k_m_(STATE_IDX::Theta)),
                                          std::cos(X_k_m_(STATE_IDX::Theta)));
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

            const double n_samples = static_cast<double>(gz_readings.size());
            gyro_bias_(0) = x_sum / n_samples;
            gyro_bias_(1) = y_sum / n_samples;
            gyro_bias_(2) = z_sum / n_samples;
            bias_samples_ = gz_readings.size();

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
