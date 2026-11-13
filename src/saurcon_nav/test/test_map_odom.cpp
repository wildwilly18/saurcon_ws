// map -> odom correction from poses at a common time (review finding 3).
#include "map_odom.hpp"

#include <cmath>
#include <cstdio>
#include <cstdlib>

using namespace saurcon_nav;

static int failures = 0;
#define CHECK(cond, ...) do { if (!(cond)) { std::printf("FAIL %s:%d: ", __FILE__, __LINE__); \
    std::printf(__VA_ARGS__); std::printf("\n"); ++failures; } } while (0)

static bool near(const Pose2& a, const Pose2& b, double tol = 1e-9) {
    return std::fabs(a.x - b.x) < tol && std::fabs(a.y - b.y) < tol && std::fabs(wrapAngle(a.th - b.th)) < tol;
}

// A car driving at 5 m/s, turning at 0.8 rad/s (pose at time t).
static Pose2 trajectory(double t) {
    const double v = 5.0, w = 0.8;
    return {v / w * std::sin(w * t), v / w * (1 - std::cos(w * t)), w * t};
}

int main() {
    // The case from the review: global x = 10 at t = 2.0, latest odometry x = 9.5 at t = 1.9.
    // Mixing those (old formula) gives a 0.5 m correction although the estimates agree.
    {
        const Pose2 mixed = mapToOdom({10, 0, 0}, {9.5, 0, 0});
        CHECK(std::fabs(mixed.x - 0.5) < 1e-12, "old formula reproduces the reported 0.5 m error");
        PoseHistory h;
        for (int k = 0; k <= 10; ++k) h.add(1.8 + 0.02 * k, {5.0 * (1.8 + 0.02 * k) / 1.0 * 1.0 - 0.0, 0, 0});
        // global x(t) = 5 t: x(1.9) = 9.5, x(2.0) = 10
        Pose2 g;
        CHECK(h.at(1.9, g), "pose at 1.9 s available");
        const Pose2 mo = mapToOdom(g, {9.5, 0, 0});
        CHECK(near(mo, {0, 0, 0}, 1e-9), "same-time correction is identity, got %.3f %.3f %.3f", mo.x, mo.y, mo.th);
    }

    // Identical global and odometry trajectories, odometry delivered 0-120 ms late, while
    // driving and turning: the correction stays identity.
    {
        PoseHistory h;
        for (int k = 0; k < 200; ++k) {
            const double now = 0.02 * k;
            h.add(now, trajectory(now));
            for (double lag : {0.0, 0.013, 0.05, 0.12}) {
                const double t_odom = now - lag;
                if (t_odom < 0.0) continue;
                Pose2 g;
                if (!h.at(t_odom, g)) { CHECK(k * 0.02 < lag + 1e-9, "history missing at %.3f", t_odom); continue; }
                const Pose2 mo = mapToOdom(g, trajectory(t_odom));
                // linear interpolation of a 5 m/s, 0.8 rad/s arc over 20 ms: sub-millimetre error
                CHECK(near(mo, {0, 0, 0}, 2e-3), "identity at t=%.2f lag=%.3f: %.4f %.4f %.4f", now, lag, mo.x, mo.y, mo.th);
            }
        }
    }

    // With a real offset between map and odom: map -> odom -> base_link equals the global pose
    // at the shared timestamp.
    {
        const Pose2 offset{1.5, -0.7, 0.4};                   // true map -> odom
        PoseHistory h;
        for (int k = 0; k < 100; ++k) h.add(0.02 * k, compose(offset, trajectory(0.02 * k)));
        const double t_odom = 1.37;                           // between samples
        Pose2 g; CHECK(h.at(t_odom, g), "pose available");
        const Pose2 odom_base = trajectory(t_odom);
        const Pose2 mo = mapToOdom(g, odom_base);
        CHECK(near(mo, offset, 2e-3), "recovered offset %.4f %.4f %.4f", mo.x, mo.y, mo.th);
        CHECK(near(compose(mo, odom_base), g, 1e-9), "map->odom->base equals the global pose");
    }

    // Out-of-order insertion, and history that does not reach the requested time.
    {
        PoseHistory h(1.0, 0.03);
        h.add(1.00, {1, 0, 0}); h.add(1.04, {3, 0, 0}); h.add(1.02, {2, 0, 0});
        Pose2 g;
        CHECK(h.at(1.01, g) && std::fabs(g.x - 1.5) < 1e-12, "out-of-order samples interpolate in time order");
        CHECK(!h.at(0.5, g), "older than the history: unavailable");
        CHECK(!h.at(1.2, g), "newer than the history beyond tolerance: unavailable");
        CHECK(h.at(1.06, g) && g.x == 3, "just past the newest sample: held");
        h.add(5.0, {9, 0, 0});
        CHECK(!h.at(1.02, g), "old samples dropped after the span");
        h.add(0.1, {7, 0, 0});                                 // clock went backwards (sim reset)
        CHECK(h.at(0.1, g) && g.x == 7 && !h.at(5.0, g), "history restarts after a clock reset");
    }

    // Angle wrap across +-pi.
    {
        PoseHistory h;
        h.add(0.0, {0, 0, 3.1}); h.add(0.02, {0, 0, -3.1});
        Pose2 g; CHECK(h.at(0.01, g) && std::fabs(std::fabs(g.th) - M_PI) < 1e-9, "interpolates the short way round");
    }

    if (failures) { std::printf("%d failure(s)\n", failures); return EXIT_FAILURE; }
    std::printf("map_odom: all checks passed\n");
    return EXIT_SUCCESS;
}
