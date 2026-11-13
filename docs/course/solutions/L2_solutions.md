# Lecture 2 — Solutions

### 2.1 [T] 1280-px stream

$f_x = 640/\tan(0.602) = 931.4$ px. By (2.4), $\sigma_Z = Z^2\sigma_d/(fB)$: doubling $f$ halves the
depth error for the same disparity error *in pixels*, from 7.4 cm to 3.7 cm at 5 m with
$\sigma_d = 0.1$ px. Strong answers add that $\sigma_d$ in pixels is not constant across
resolutions: matching noise grows somewhat at higher resolution, and the device's stereo pair, not
the colour camera, sets $f$ in (2.4).

### 2.2 [C] Marker size in the image

The width is $f s/Z$ with $s = 0.122$ m (reference script):

| Range | Width | 0.3 px corner noise, laterally |
|---|---|---|
| 1 m | 56.8 px | 0.6 mm |
| 3 m | 18.9 px | 1.9 mm |
| 5 m | 11.4 px | 3.2 mm |

Lateral position is well determined at every range. Orientation is not: its error scales as corner
noise over marker width, $\approx 0.3/11.4 \approx 0.026$ rad at 5 m, about 1.5°, before the planar
ambiguity (2.4) is considered. By (2.3)/2.3 that is ≈ 13 cm of vehicle error at 5 m.

### 2.3 [T] Lateral error from a yaw error

Write ${}^{C}T_{M} = (\mathbf C, \mathbf t)$, so $({}^{C}T_{M})^{-1} = (\mathbf C^\top, -\mathbf
C^\top\mathbf t)$: the camera's position in the marker frame is $-\mathbf C^\top\mathbf t$. A yaw error
$\epsilon$ replaces $\mathbf C$ by $\mathbf C\,\mathbf R(\epsilon)$, so the camera position becomes
$-\mathbf R(-\epsilon)\mathbf C^\top\mathbf t$: the same vector rotated by $-\epsilon$ about the marker
origin. A rotation by $\epsilon$ moves a point at distance $r = \|\mathbf t\|$ by $2r\sin(\epsilon/2)
\approx \epsilon r$, perpendicular to the line of sight. The constant mount ${}^{B}T_{C}$ and the map
transform ${}^{W}T_{M}$ carry this displacement into the world unchanged in magnitude.

### 2.4 [C] When IPPE's two solutions become indistinguishable

**Method.** Monte Carlo: for each range, project the corners with a known pose, add $\mathcal N(0,
0.3^2)$ px noise 200 times, solve with `SOLVEPNP_IPPE_SQUARE`, and record the ratio of the two
solutions' reprojection errors. Call them indistinguishable when the ratio's distribution straddles
1 (for example, when more than 20% of trials pick the wrong solution).

**Reference.** Notebook 02, cell 9 (true yaw 10°): at 1 m the errors are 0.125 vs 0.486 px (clearly
separable); at 3 m 0.085 vs 0.108 px (ratio 1.27, frequently confused under noise); at 5 m 0.036 vs
0.039 px, and the *wrong* (mirrored) solution was ranked first. Expected answer: indistinguishable
from about **3–4 m** for a 0.122 m marker with 0.3 px noise; the exact range depends on yaw (head-on
views are worst).

### 2.5 [T] Stationary time for bias estimation

See the lecture's answer: about 8,600 samples, 86 s. Full credit requires noting that the error
contributed is $t\sigma_n/\sqrt N$, linear in run length, so the requirement scales with the
*square* of the run duration.

### 2.6 [T] Depth alignment chain

For each valid depth pixel $(u, v)$ with depth $Z$ in the left mono camera $\{L\}$:

1. back-project: ${}^{L}\mathbf p = Z\,K_L^{-1}(u, v, 1)^\top$ (after undistortion);
2. transform: ${}^{RGB}\mathbf p = {}^{RGB}T_{L}\,{}^{L}\mathbf p$, with ${}^{RGB}T_{L}$ from the device's
   factory extrinsics;
3. project: $(u', v') = \pi(K_{RGB}\,{}^{RGB}\mathbf p)$, then distort with the colour camera's model;
4. splat with a z-buffer: if several points land on one colour pixel, keep the nearest.

**Holes at boundaries** come from two sources. *Disocclusion*: colour pixels next to a foreground
object see background that the left camera could not see (it was hidden behind the object from the
left camera's viewpoint, 3–4 cm away), so no depth maps there. *Stereo invalidation*: the left–right
consistency check rejects pixels near depth discontinuities, where left and right views see different
surfaces. Step 4 also leaves gaps where the forward warp spreads points apart (magnified surfaces);
those are filled by interpolation in some pipelines, which is wrong exactly at boundaries. Small
cones are mostly boundary, which is why their depth is so often missing (Lecture 9 §2).
