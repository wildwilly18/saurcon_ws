# UKF Measurement Update — Study Reference

## Context: Where This Fits in the UKF Cycle

```
┌─────────────────────────────────────────────────────────────┐
│  PREDICTION (predictionUpdate)                              │
│  Uses: X_k_p_, P_k_p_  (posterior from previous step)      │
│  Generates sigma points → propagate through f(x)           │
│  Writes: X_k_m_, P_k_m_  (predicted mean & covariance)     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  MEASUREMENT UPDATE (measurementUpdate)                     │
│  Uses: X_k_m_, P_k_m_  (predicted state)                   │
│  Uses: z  (actual sensor measurement)                       │
│  Writes: X_k_p_, P_k_p_  (new posterior)                   │
└─────────────────────────────────────────────────────────────┘
```

**State vector**: `[X, Y, Theta, V]`  (n = 4)
**Measurement vector** (ArUco): `[X, Y, Theta]`  (m = 3)
**Sigma points**: 2n+1 = 9 columns

---

## Step 1 — Generate Sigma Points from the Predicted State

Regenerate sigma points from **X_k_m_** and **P_k_m_** (not from X_k_p_).

**Cholesky factor:**
$$L = \text{chol}\big((n + \lambda) \cdot P_{k|k-1}\big)$$

**Sigma point matrix** (4×9):
$$\mathcal{X}_0 = \hat{x}_{k|k-1}$$
$$\mathcal{X}_i = \hat{x}_{k|k-1} + L_{:,i} \quad i = 1 \ldots n$$
$$\mathcal{X}_{i+n} = \hat{x}_{k|k-1} - L_{:,i} \quad i = 1 \ldots n$$

> **Why**: The sigma points encode the uncertainty in the predicted state. Using **P_k_m_** (not the old P_k_p_) is critical — you need the uncertainty *after* the prediction step.

```cpp
Eigen::MatrixXd Lm = ((n_ + lambda_) * P_k_m_).llt().matrixL();
Eigen::MatrixXd sp(n_, 2*n_+1);
sp.col(0) = X_k_m_;
for(int i = 0; i < n_; i++){
    sp.col(i+1)    = X_k_m_ + Lm.col(i);
    sp.col(i+1+n_) = X_k_m_ - Lm.col(i);
}
```

---

## Step 2 — Project Sigma Points Through the Measurement Function h(x)

The measurement function extracts the observable states:
$$h(x) = [X,\; Y,\; \Theta]$$

For this system h is linear, so projection is just extracting the top 3 rows:

$$\mathcal{Z}_i = h(\mathcal{X}_i) \quad \Rightarrow \quad z_{sp} = \mathcal{X}[0:3,\; :]$$

```cpp
Eigen::MatrixXd z_sp = sp.topRows<3>();   // 3×9
```

> **Why**: This is the UKF's nonlinear-safe way of computing what the sensor *should* see given each sigma point state. For a nonlinear h, you'd evaluate h(σᵢ) individually; here it reduces to a row slice.

---

## Step 3 — Predicted Measurement Mean ẑ

Weighted sum of the projected sigma points:
$$\hat{z} = \sum_{i=0}^{2n} W_m^i \cdot \mathcal{Z}_i = z_{sp} \cdot W_m$$

```cpp
Eigen::Vector3d z_hat = z_sp * Wm_;   // 3×9 · 9×1 = 3×1
```

---

## Step 4 — Innovation Vector

The difference between what was actually measured and what was predicted:
$$\nu = z_{meas} - \hat{z}$$

**Angle wrap is required on the θ component** — raw subtraction can produce errors > π:
$$\nu_\theta = \text{atan2}\!\big(\sin(\theta_{meas} - \hat{z}_\theta),\; \cos(\theta_{meas} - \hat{z}_\theta)\big)$$

```cpp
Eigen::Vector3d innov;
innov(0) = loc_measure.x     - z_hat(0);
innov(1) = loc_measure.y     - z_hat(1);
innov(2) = std::atan2(std::sin(loc_measure.theta - z_hat(2)),
                       std::cos(loc_measure.theta - z_hat(2)));
```

---

## Step 5 — Centered Measurement Sigma Points (dZ)

Deviation of each projected sigma point from the predicted measurement mean:
$$\delta Z_i = \mathcal{Z}_i - \hat{z}$$

**Wrap the θ row** (row 2) of dZ — same reason as the innovation:

```cpp
Eigen::MatrixXd dZ = z_sp.colwise() - z_hat;   // 3×9
for(int i = 0; i < 2*n_+1; i++){
    dZ(2,i) = std::atan2(std::sin(dZ(2,i)), std::cos(dZ(2,i)));
}
```

---

## Step 6 — Innovation Covariance Sₖ

Weighted outer-product sum of the measurement deviations, plus sensor noise R:
$$S_k = \sum_{i=0}^{2n} W_c^i \cdot \delta Z_i \cdot \delta Z_i^T + R = dZ \cdot \text{diag}(W_c) \cdot dZ^T + R$$

R is the sensor noise covariance for [X, Y, Θ] — sourced from the ArUco localizer's reported variances.

```cpp
Eigen::Matrix3d S_z = dZ * Wc_.asDiagonal() * dZ.transpose() + R;   // 3×3
```

> **Physical meaning**: How spread out are the predicted measurements? Large Sₖ → high prediction uncertainty → filter trusts the measurement more. Small Sₖ → filter trusts its prediction.

---

## Step 7 — Cross-Covariance Pₓᵤ

Correlation between **state** spread and **measurement** spread:
$$P_{xz} = \sum_{i=0}^{2n} W_c^i \cdot \delta X_i \cdot \delta Z_i^T = dX \cdot \text{diag}(W_c) \cdot dZ^T$$

where $\delta X_i = \mathcal{X}_i - \hat{x}_{k|k-1}$.

```cpp
Eigen::MatrixXd dX  = sp.colwise() - X_k_m_;                          // 4×9
Eigen::MatrixXd P_xz = dX * Wc_.asDiagonal() * dZ.transpose();        // 4×3
```

> **Physical meaning**: How much does each state dimension contribute to each measurement dimension? This is what allows the filter to update the unobserved state V from the X/Y/Θ measurement.

---

## Step 8 — Kalman Gain K

$$K = P_{xz} \cdot S_k^{-1}$$

```cpp
Eigen::MatrixXd K = P_xz * S_z.inverse();   // 4×3
```

> **Physical meaning**: How much to trust the measurement vs. the prediction. K scales the innovation into a 4D state correction. Large Sₖ (uncertain prediction) → large K → trust measurement more.

---

## Step 9 — State Update

$$\hat{x}_{k|k} = \hat{x}_{k|k-1} + K \cdot \nu$$

**Wrap θ after update** — K·ν can push Theta outside (−π, π]:

```cpp
X_k_p_ = X_k_m_ + K * innov;
X_k_p_(STATE_IDX::Theta) = std::atan2(std::sin(X_k_p_(STATE_IDX::Theta)),
                                        std::cos(X_k_p_(STATE_IDX::Theta)));
```

---

## Step 10 — Covariance Update

$$P_{k|k} = P_{k|k-1} - K \cdot S_k \cdot K^T$$

```cpp
P_k_p_ = P_k_m_ - K * S_z * K.transpose();   // 4×4
```

> **Note on Joseph form**: The classic Joseph form `(I−KH)P(I−KH)ᵀ + KRKᵀ` requires explicit H. In the UKF, Sₖ implicitly encodes `HPHᵀ + R` through the sigma points, so `K·Sₖ·Kᵀ` is the equivalent expression. The standard form above is numerically sufficient when P remains well-conditioned.

---

## UKF Tuning Parameters

| Parameter | Role | Effect of increasing |
|-----------|------|----------------------|
| `alpha` (0.1) | Sigma point spread | Spreads sigma points further from mean |
| `beta` (2.0) | Prior distribution knowledge | 2.0 is optimal for Gaussian |
| `kappa` (0.0) | Secondary scaling | Usually 0 |
| `lambda` | Derived: α²(n+κ)−n | Controls weight on central sigma point |
| `gyro_q_std` | Process noise on Θ | More: filter trusts gyro less |
| `odom_q_std` | Process noise on V | More: filter trusts odometry less |
| `var_x/y/theta` | Measurement noise R | Passed in from ArUco localizer |

---

## Weights Summary

$$W_m^0 = \frac{\lambda}{n+\lambda}, \quad W_c^0 = W_m^0 + (1 - \alpha^2 + \beta)$$
$$W_m^i = W_c^i = \frac{1}{2(n+\lambda)}, \quad i = 1 \ldots 2n$$

The mean weights sum to 1. The covariance weights can be negative for W_c^0 when alpha is small — this is expected and allows the UKF to capture higher-order moments.

---

## Complete Flow (one update cycle)

```
predictionUpdate(dt)
    → generateSigmaPoints()          from X_k_p_, P_k_p_
    → propagate through f(x)         CTRV model
    → recover X_k_m_, P_k_m_

measurementUpdate()
    → check fresh_localization
    → sigma points from X_k_m_, P_k_m_
    → project through h(x) → z_sp
    → z_hat = z_sp * Wm
    → innov = z_meas - z_hat         (wrap theta)
    → dZ = z_sp - z_hat              (wrap theta row)
    → S_z = dZ*diag(Wc)*dZ' + R
    → dX = sp - X_k_m_
    → P_xz = dX*diag(Wc)*dZ'
    → K = P_xz * S_z^-1
    → X_k_p_ = X_k_m_ + K * innov   (wrap theta)
    → P_k_p_ = P_k_m_ - K*S_z*K'
    → last_localization_time = stamp
```
