// Planar pose helpers and the map -> odom correction, kept free of ROS so they can be tested.
#pragma once

#include <cmath>
#include <deque>
#include <iterator>
#include <utility>

namespace saurcon_nav {

struct Pose2 { double x{0}, y{0}, th{0}; };

inline double wrapAngle(double a) { return std::atan2(std::sin(a), std::cos(a)); }

inline Pose2 compose(const Pose2& a, const Pose2& b) {            // a ⊕ b
    const double c = std::cos(a.th), s = std::sin(a.th);
    return {a.x + c * b.x - s * b.y, a.y + s * b.x + c * b.y, wrapAngle(a.th + b.th)};
}

inline Pose2 inverse(const Pose2& a) {
    const double c = std::cos(a.th), s = std::sin(a.th);
    return {-c * a.x - s * a.y, s * a.x - c * a.y, -a.th};
}

inline Pose2 interpolate(const Pose2& a, const Pose2& b, double f) {
    return {a.x + f * (b.x - a.x), a.y + f * (b.y - a.y), wrapAngle(a.th + f * wrapAngle(b.th - a.th))};
}

// map -> odom from the global pose (map -> base_link) and the odometry pose (odom -> base_link).
// Both must describe the car at the same instant: mixing poses from different times builds the
// car's motion in between into the correction.
inline Pose2 mapToOdom(const Pose2& map_base, const Pose2& odom_base) {
    return compose(map_base, inverse(odom_base));
}

// Recent global poses by time, so the global pose can be evaluated at the (older) stamp of the
// latest odometry transform.
class PoseHistory {
public:
    explicit PoseHistory(double span = 1.0, double edge_tolerance = 0.03)
        : span_(span), tol_(edge_tolerance) {}

    void add(double t, const Pose2& p) {
        if (!h_.empty() && t < h_.back().first - span_) h_.clear();   // clock went backwards (sim reset)
        auto it = h_.end();
        while (it != h_.begin() && std::prev(it)->first > t) --it;   // keep sorted (out-of-order input)
        if (it != h_.begin() && std::prev(it)->first == t) std::prev(it)->second = p;
        else h_.insert(it, {t, p});
        while (!h_.empty() && h_.back().first - h_.front().first > span_) h_.pop_front();
    }

    // Pose at time t, interpolated. Outside the stored span only within edge_tolerance of
    // either end (held constant); otherwise false: the pose at that time is not known.
    bool at(double t, Pose2& out) const {
        if (h_.empty()) return false;
        if (t <= h_.front().first) {
            if (h_.front().first - t > tol_) return false;
            out = h_.front().second; return true;
        }
        if (t >= h_.back().first) {
            if (t - h_.back().first > tol_) return false;
            out = h_.back().second; return true;
        }
        for (size_t k = 1; k < h_.size(); ++k) {
            if (h_[k].first >= t) {
                const auto& a = h_[k - 1]; const auto& b = h_[k];
                const double f = (t - a.first) / (b.first - a.first);
                out = interpolate(a.second, b.second, f);
                return true;
            }
        }
        return false;
    }

    bool empty() const { return h_.empty(); }

private:
    double span_, tol_;
    std::deque<std::pair<double, Pose2>> h_;
};

}  // namespace saurcon_nav
