#!/usr/bin/env python3
"""Generate the lecture figures in docs/course/figures/.

Deterministic; every quantitative figure is computed from the formulas in the lectures or from
the workspace's own code (track geometry, the classical follower). Run from the workspace root:

  PYTHONPATH=src/saurcon_plan:$PYTHONPATH .venv-rl/bin/python docs/course/figures/make_figures.py
"""
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle, Ellipse, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parent
WS = OUT.parents[2]
sys.path.insert(0, str(WS / 'src' / 'saurcon_plan'))

# Palette (validated categorical order) and neutral inks
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = (
    '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948')
INK, INK2, MUTED, GRID, SURF = '#0b0b0b', '#52514e', '#8d8b86', '#e4e3df', '#ffffff'
plt.rcParams.update({
    'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
    'axes.edgecolor': '#c9c7c1', 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'text.color': INK, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
    'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 10, 'axes.titlesize': 11,
    'axes.titleweight': 'bold', 'axes.titlelocation': 'left', 'legend.frameon': False,
    'lines.linewidth': 2.0, 'font.family': 'DejaVu Sans'})


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('wrote', name)


def arrow(ax, p, q, color=INK2, lw=1.4, style='-|>', ms=10, ls='-'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, linestyle=ls))


def wheel(ax, c, ang, length=0.32, width=0.12, color=INK):
    c = np.asarray(c, float)
    d = np.array([math.cos(ang), math.sin(ang)]); n = np.array([-d[1], d[0]])
    pts = [c + d * length / 2 + n * width / 2, c - d * length / 2 + n * width / 2,
           c - d * length / 2 - n * width / 2, c + d * length / 2 - n * width / 2]
    ax.add_patch(Polygon(pts, closed=True, color=color, zorder=5))


def schematic(ax):
    ax.set_aspect('equal'); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])


# 1.1 Ackermann geometry and the kinematic bicycle --------------------------------------------
def fig_ackermann():
    L, T, rho = 1.0, 0.7, 2.0
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.2))
    ax = axs[0]; schematic(ax)
    icr = np.array([0.0, rho])
    rl, rr, fl, fr = (0, T / 2), (0, -T / 2), (L, T / 2), (L, -T / 2)
    ax.plot([-0.4, 0.0], [0, 0], color=MUTED, lw=1, ls=':')
    ax.plot([0, 0], [-T / 2, rho], color=MUTED, lw=1, ls='--')          # rear axle extension
    for w in (fl, fr):
        ax.plot([w[0], icr[0]], [w[1], icr[1]], color=MUTED, lw=1, ls='--')
    ax.add_patch(Rectangle((-0.15, -T / 2), L + 0.3, T, fill=False, ec=INK2, lw=1.2))
    d_in, d_out = math.atan(L / (rho - T / 2)), math.atan(L / (rho + T / 2))
    wheel(ax, rl, 0); wheel(ax, rr, 0); wheel(ax, fl, d_in, color=BLUE); wheel(ax, fr, d_out, color=BLUE)
    ax.plot(*icr, 'o', color=ORANGE, ms=8, zorder=6); ax.text(icr[0] + 0.08, icr[1] + 0.05, 'ICR', color=ORANGE, weight='bold')
    ax.plot(0, 0, 'o', color=INK, ms=6, zorder=6); ax.text(-0.58, -0.08, '{B}', color=INK2, fontsize=10)
    ax.annotate('', (0.05, rho), (0.05, 0.0), arrowprops=dict(arrowstyle='<->', color=INK2))
    ax.text(0.1, rho / 2, r'$\rho$', fontsize=13, color=INK)
    ax.annotate('', (L, -T / 2 - 0.25), (0, -T / 2 - 0.25), arrowprops=dict(arrowstyle='<->', color=INK2))
    ax.text(L / 2 - 0.05, -T / 2 - 0.42, r'$L$', fontsize=13)
    ax.text(L + 0.25, T / 2 + 0.1, r'$\delta_\mathrm{in}$', color=BLUE, fontsize=13)
    ax.text(L + 0.25, -T / 2 - 0.15, r'$\delta_\mathrm{out}$', color=BLUE, fontsize=13)
    ax.set_xlim(-0.6, 2.0); ax.set_ylim(-1.0, rho + 0.35)
    ax.set_title('(a) Ackermann: each wheel normal to the ICR', fontsize=10.5)
    ax = axs[1]; schematic(ax)
    delta = 0.45; rho2 = L / math.tan(delta)
    icr2 = np.array([0.0, rho2])
    th = np.linspace(-0.25, 1.1, 100)
    ax.plot(icr2[0] + rho2 * np.sin(th), icr2[1] - rho2 * np.cos(th), color=AQUA, lw=2, label='rear-axle path')
    ax.plot([0, L], [0, 0], color=INK2, lw=3)
    wheel(ax, (0, 0), 0); wheel(ax, (L, 0), delta, color=BLUE)
    ax.plot([0, 0], [0, rho2], color=MUTED, ls='--', lw=1); ax.plot([L, 0], [0, rho2], color=MUTED, ls='--', lw=1)
    ax.plot(*icr2, 'o', color=ORANGE, ms=8); ax.text(icr2[0] + 0.08, icr2[1], 'ICR', color=ORANGE, weight='bold')
    arrow(ax, (0, 0), (0.55, 0), color=INK, lw=2); ax.text(0.3, -0.22, r'$v$ along $\psi$', fontsize=11)
    arrow(ax, (L, 0), (L + 0.5 * math.cos(delta), 0.5 * math.sin(delta)), color=BLUE, lw=2)
    ax.text(L + 0.45, 0.35, r'$\delta$', color=BLUE, fontsize=13)
    ax.text(-0.75, rho2 / 2, r'$\rho = L/\tan\delta$', fontsize=11)
    ax.text(0.55, rho2 - 0.25, r'$\dot\psi = v/\rho = v\tan\delta/L$', fontsize=11)
    ax.set_xlim(-0.9, 2.3); ax.set_ylim(-0.6, rho2 + 0.35)
    ax.set_title('(b) Kinematic bicycle: no sideslip at the rear axle', fontsize=10.5)
    save(fig, 'ackermann_bicycle.png')


# 1.2 Friction circle and ellipse ---------------------------------------------------------------
def fig_friction():
    mg, k = 10.0, 1.5
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(mg * np.cos(t), mg * np.sin(t), color=MUTED, lw=1.5, ls='--', label=r'friction circle $\sqrt{a_x^2+a_y^2}\leq\mu g$')
    ax_ = mg * np.cos(t); ay_ = mg * np.sin(t)
    ax_ = np.where(ax_ < 0, ax_ / k, ax_)
    ax.fill(ax_, ay_, color=BLUE, alpha=0.12, lw=0)
    ax.plot(ax_, ay_, color=BLUE, lw=2, label=r'training ellipse, braking weighted $k=1.5$')
    ax.axhline(0, color=INK2, lw=0.8); ax.axvline(0, color=INK2, lw=0.8)
    ax.text(-9.5, 0.6, 'braking', color=INK2); ax.text(5.6, 0.6, 'accelerating', color=INK2)
    ax.text(-4.2, 10.5, 'cornering', color=INK2)
    ax.set_xlabel(r'$a_x$ (m/s²)'); ax.set_ylabel(r'$a_y$ (m/s²)'); ax.set_aspect('equal')
    ax.set_xlim(-11.5, 11.5); ax.set_ylim(-11.5, 11.5)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.32), fontsize=9)
    ax.set_title('Admissible accelerations (1.9)')
    save(fig, 'friction_ellipse.png')


# 1.3 Minimum-time speed profile on the racetrack ------------------------------------------------
def fig_speed_profile():
    from saurcon_plan.track import Track
    tr = Track.from_world(WS / 'src/middle_earth/worlds/racetrack.world')
    s, kap = tr.s, np.abs(tr.curvature)
    mg, a, b, vmax = 10.0, 3.8, 4.0, 12.0
    vbar2 = np.minimum(mg / np.maximum(kap, 1e-6), vmax ** 2)
    ds = np.diff(np.append(s, tr.length))
    # periodic: run passes twice around the loop
    n = len(s)
    v2 = vbar2.copy()
    fwd = v2.copy()
    for _ in range(2):
        for i in range(n):
            j = (i + 1) % n
            fwd[j] = min(fwd[j], fwd[i] + 2 * a * ds[i])
    v2 = fwd.copy()
    for _ in range(2):
        for i in range(n - 1, -1, -1):
            j = (i + 1) % n
            v2[i] = min(v2[i], v2[j] + 2 * b * ds[i])
    v = np.sqrt(v2); T = float(np.sum(ds / np.maximum(v, 1e-3)))
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(s, np.sqrt(vbar2), color=MUTED, lw=1.4, ls='--', label=r'cornering limit $\sqrt{\mu g/|\kappa|}$')
    ax.plot(s, np.sqrt(fwd), color=ORANGE, lw=1.4, label=f'after forward pass ($a$ = {a} m/s²)')
    ax.plot(s, v, color=BLUE, lw=2.2, label=f'after backward pass ($b$ = {b} m/s²): lap {T:.2f} s')
    ax.set_xlabel('arc length $s$ along the centreline (m)'); ax.set_ylabel('speed (m/s)')
    ax.set_ylim(0, 13); ax.set_xlim(0, tr.length)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), fontsize=9, ncol=3)
    ax.set_title('Algorithm 1.1 on the racetrack centreline (μg = 10 m/s²)')
    save(fig, 'speed_profile.png')
    return T


# 2.1 / 9.1 Ranging sensitivity -----------------------------------------------------------------
def fig_ranging():
    Z = np.linspace(0.3, 6.5, 200)
    f, B, h, hc = 465.7, 0.075, 0.137, 0.071
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(Z, 100 * Z ** 2 / (f * B), color=VIOLET, label='stereo, per 1 px disparity  $Z^2/(fB)$')
    ax.plot(Z, 100 * Z ** 2 / (f * hc), color=ORANGE, label=r'size, per 1 px blob height  $Z^2/(f h_\mathrm{cone})$')
    ax.plot(Z, 100 * Z ** 2 / (f * h), color=BLUE, label='ground plane, per 1 px base row  $Z^2/(f h)$')
    meas_z, meas_e = [1.25, 3.0, 5.25], [3, 5, 8]
    ax.plot(meas_z, meas_e, 'o', color=BLUE, mfc=SURF, mew=2, ms=8, label='ground plane, measured in Gazebo')
    ax.set_xlabel('range $Z$ (m)'); ax.set_ylabel('range error (cm)')
    ax.set_xlim(0, 6.6); ax.set_ylim(0, 120)
    ax.legend(loc='upper left', fontsize=9)
    ax.set_title('Every camera range error grows as $Z^2$; the lever arm decides how fast')
    save(fig, 'ranging_error.png')


# 3.1 The unscented transform -------------------------------------------------------------------
def fig_unscented():
    rng = np.random.default_rng(3)
    mu = np.array([1.0, np.pi / 2]); P = np.diag([0.02 ** 2, 0.35 ** 2])
    g = lambda x: np.array([x[0] * np.cos(x[1]), x[0] * np.sin(x[1])])
    S = rng.multivariate_normal(mu, P, 20000)
    Y = np.column_stack([S[:, 0] * np.cos(S[:, 1]), S[:, 0] * np.sin(S[:, 1])])
    m_mc, C_mc = Y.mean(0), np.cov(Y.T)
    # linearisation
    J = np.array([[np.cos(mu[1]), -mu[0] * np.sin(mu[1])], [np.sin(mu[1]), mu[0] * np.cos(mu[1])]])
    m_lin, C_lin = g(mu), J @ P @ J.T
    # unscented (alpha=1, beta=2, kappa=1)
    n, alpha, beta, kappa = 2, 1.0, 2.0, 1.0
    lam = alpha ** 2 * (n + kappa) - n
    Ls = np.linalg.cholesky((n + lam) * P)
    X = [mu] + [mu + Ls[:, i] for i in range(n)] + [mu - Ls[:, i] for i in range(n)]
    Wm = np.full(2 * n + 1, 1 / (2 * (n + lam))); Wm[0] = lam / (n + lam)
    Wc = Wm.copy(); Wc[0] += 1 - alpha ** 2 + beta
    GY = np.array([g(x) for x in X]); m_ut = Wm @ GY
    C_ut = sum(Wc[i] * np.outer(GY[i] - m_ut, GY[i] - m_ut) for i in range(2 * n + 1))

    def ell(ax, m, C, color, label, ls='-'):
        w, V = np.linalg.eigh(C); ang = math.degrees(math.atan2(V[1, 1], V[0, 1]))
        ax.add_patch(Ellipse(m, 2 * 2 * math.sqrt(w[1]), 2 * 2 * math.sqrt(w[0]), angle=ang, fill=False,
                             ec=color, lw=2, ls=ls, label=label))
        ax.plot(*m, 'o' if ls == '-' else 's', color=color, ms=7)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ax.scatter(Y[::8, 0], Y[::8, 1], s=2, color=MUTED, alpha=0.35, label='Monte-Carlo samples', rasterized=True)
    ell(ax, m_mc, C_mc, INK, 'true mean and 2σ (Monte Carlo)')
    ell(ax, m_lin, C_lin, ORANGE, 'linearised (EKF)', ls='--')
    ell(ax, m_ut, C_ut, BLUE, 'unscented transform')
    ax.plot(GY[:, 0], GY[:, 1], 'x', color=BLUE, ms=9, mew=2, label='transformed sigma points')
    ax.set_aspect('equal'); ax.set_xlabel('$x$'); ax.set_ylabel('$y$')
    ax.set_xlim(-0.9, 0.9); ax.set_ylim(0.45, 1.15)
    ax.legend(loc='lower center', fontsize=8.5, ncol=2, bbox_to_anchor=(0.5, -0.42))
    ax.set_title('Polar → Cartesian: range σ = 2 cm, bearing σ = 0.35 rad')
    save(fig, 'unscented_transform.png')
    return m_mc, m_lin, m_ut


# 4.1 Pose graph and the sparsity of H ------------------------------------------------------------
def fig_pose_graph():
    N = 28
    t = np.linspace(0, 2 * np.pi * 1.08, N)
    rng = np.random.default_rng(1)
    drift = np.cumsum(rng.normal(0, 0.035, (N, 2)), axis=0) + np.outer(np.linspace(0, 1, N), [0.25, -0.15])
    xy = np.column_stack([2.2 * np.cos(t), 1.3 * np.sin(t)]) + drift
    closures = [(0, N - 2), (1, N - 1), (3, 17)]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={'width_ratios': [1.35, 1]})
    ax = axs[0]; schematic(ax)
    for i in range(N - 1):
        ax.plot(xy[i:i + 2, 0], xy[i:i + 2, 1], color=INK2, lw=1.6, zorder=1)
    for (i, j) in closures[:2]:
        ax.plot(*zip(xy[i], xy[j]), color=AQUA, lw=2.2, ls='--', zorder=2)
    i, j = closures[2]
    ax.plot(*zip(xy[i], xy[j]), color=RED, lw=2.2, ls=':', zorder=2)
    ax.scatter(xy[:, 0], xy[:, 1], s=46, color=BLUE, zorder=3, edgecolor=SURF, linewidth=1.2)
    ax.scatter(*xy[0], s=110, color=INK, marker='s', zorder=4)
    ax.text(xy[0, 0] - 1.45, xy[0, 1] - 0.05, r'$\mathbf{x}_0$ fixed (gauge)', fontsize=9, color=INK2)
    ax.plot([], [], color=INK2, lw=1.6, label='odometry factor $\\mathbf{z}_{i,i+1}$')
    ax.plot([], [], color=AQUA, lw=2.2, ls='--', label='loop closure (true)')
    ax.plot([], [], color=RED, lw=2.2, ls=':', label='loop-closure candidate (false)')
    ax.legend(loc='center', fontsize=9)
    ax.set_title('(a) Pose graph: nodes are poses, edges are factors', fontsize=10.5)
    ax = axs[1]
    H = np.zeros((N, N))
    for k in range(N):
        H[k, k] = 1
    for k in range(N - 1):
        H[k, k + 1] = H[k + 1, k] = 1
    for (a, b_) in closures[:2]:
        H[a, b_] = H[b_, a] = 2
    a, b_ = closures[2]; H[a, b_] = H[b_, a] = 3
    from matplotlib.colors import ListedColormap
    ax.imshow(H, cmap=ListedColormap([SURF, INK2, AQUA, RED]), interpolation='nearest', vmin=0, vmax=3)
    ax.set_xticks([0, 9, 19, N - 1]); ax.set_yticks([0, 9, 19, N - 1]); ax.grid(False)
    ax.set_xlabel('node $j$'); ax.set_ylabel('node $i$')
    ax.set_title('(b) Block pattern of $H$: banded, plus closures', fontsize=10.5)
    save(fig, 'pose_graph.png')


# 5.1 Mode logic ----------------------------------------------------------------------------------
def fig_state_machine():
    fig, ax = plt.subplots(figsize=(10.5, 4.8)); schematic(ax)
    S = {'STARTUP': (-0.2, 2.0), 'STANDBY': (3.2, 2.0), 'RUN_CONTROL': (6.6, 3.5), 'RUN_AUTONOMOUS': (6.6, 0.5),
         'FAULT': (10.0, 2.0)}
    col = {'STARTUP': MUTED, 'STANDBY': BLUE, 'RUN_CONTROL': AQUA, 'RUN_AUTONOMOUS': AQUA, 'FAULT': RED}
    W, Hh = 2.3, 0.62
    for k, (x, y) in S.items():
        ax.add_patch(FancyBboxPatch((x - W / 2, y - Hh / 2), W, Hh, boxstyle='round,pad=0.03,rounding_size=0.14',
                                    fc=SURF, ec=col[k], lw=2.2, zorder=3))
        ax.text(x, y, k, ha='center', va='center', fontsize=9.5, weight='bold', color=INK, zorder=4)

    def border(c, d):
        """Point where a ray from box centre c in direction d leaves the box."""
        tx = (W / 2 + 0.06) / abs(d[0]) if abs(d[0]) > 1e-9 else 1e9
        ty = (Hh / 2 + 0.06) / abs(d[1]) if abs(d[1]) > 1e-9 else 1e9
        return c + d * min(tx, ty)

    def edge(a, b, label, off=0.0, color=INK2, lpos=0.5, ldy=0.0):
        pa, pb = np.array(S[a], float), np.array(S[b], float)
        d = (pb - pa) / np.linalg.norm(pb - pa); n = np.array([-d[1], d[0]])
        p0, p1 = border(pa, d) + n * off, border(pb, -d) + n * off
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=13, color=color, lw=1.5, zorder=2))
        m = p0 + (p1 - p0) * lpos + n * (0.3 if off >= 0 else -0.3) + np.array([0, ldy])
        ax.text(*m, label, ha='center', va='center', fontsize=8.5, color=color, zorder=5,
                bbox=dict(fc=SURF, ec='none', pad=1.0))
    edge('STARTUP', 'STANDBY', 'RC ready', ldy=0.05)
    edge('STANDBY', 'RUN_CONTROL', 'hold menu 2 s', off=0.14, lpos=0.45)
    edge('RUN_CONTROL', 'STANDBY', 'hold menu/view 2 s', off=0.14, lpos=0.4)
    edge('STANDBY', 'RUN_AUTONOMOUS', 'hold view 2 s', off=-0.14, lpos=0.45)
    edge('RUN_AUTONOMOUS', 'STANDBY', 'hold menu/view 2 s', off=-0.14, lpos=0.4)
    edge('RUN_CONTROL', 'FAULT', 'joystick or RC lost', color=RED, off=0.0)
    edge('RUN_AUTONOMOUS', 'FAULT', 'joystick or RC lost', color=RED, off=0.0)
    # FAULT -> STANDBY, routed below the diagram
    xs, xf, yb = S['STANDBY'][0], S['FAULT'][0], -0.55
    ax.plot([xf, xf, xs], [S['FAULT'][1] - Hh / 2 - 0.06, yb, yb], color=INK2, lw=1.5, zorder=1)
    ax.add_patch(FancyArrowPatch((xs, yb), (xs, S['STANDBY'][1] - Hh / 2 - 0.06), arrowstyle='-|>',
                                 mutation_scale=13, color=INK2, lw=1.5))
    ax.text((xs + xf) / 2, yb - 0.25, 'hold view 2 s (a deliberate reset: faults are sticky)', ha='center',
            fontsize=8.5, color=INK2)
    ax.text(6.6, 4.35, 'drive commands leave only in RUN states; elsewhere a stop is sent every 30 ms',
            ha='center', fontsize=8.5, color=INK2, style='italic')
    ax.set_xlim(-1.4, 11.2); ax.set_ylim(-1.05, 4.6)
    save(fig, 'state_machine.png')


# 6.1 PPO's clipped objective ------------------------------------------------------------------------
def fig_ppo_clip():
    eps = 0.2; rho = np.linspace(0, 2, 400)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6), sharey=False)
    for ax, A, title in ((axs[0], 1.0, r'$\hat A > 0$: no gain beyond $1+\epsilon$'),
                         (axs[1], -1.0, r'$\hat A < 0$: no gain below $1-\epsilon$')):
        ax.axvspan(1 - eps, 1 + eps, color=BLUE, alpha=0.08, lw=0)
        ax.plot(rho, rho * A, color=MUTED, ls='--', lw=1.4, label=r'unclipped $\rho\hat A$')
        ax.plot(rho, np.minimum(rho * A, np.clip(rho, 1 - eps, 1 + eps) * A), color=BLUE, lw=2.4,
                label=r'$L^\mathrm{CLIP}$')
        ax.axvline(1, color=INK2, lw=0.8)
        ax.set_xlabel(r'probability ratio $\rho_t$'); ax.set_title(title, fontsize=10.5)
        ax.legend(fontsize=9, loc='upper left' if A > 0 else 'lower left')
    axs[0].set_ylabel('per-sample objective')
    save(fig, 'ppo_clip.png')


# 7.1 How much do n clean runs say? ---------------------------------------------------------------
def fig_reliability():
    from scipy.stats import beta
    n = np.arange(1, 41)
    lo_all = np.array([beta.ppf(0.025, k, 1) for k in n])                  # k = n successes
    lo_one = np.array([beta.ppf(0.025, k - 1, 2) if k > 1 else 0 for k in n])  # one failure
    fig, ax = plt.subplots(figsize=(8, 3.9))
    ax.plot(n, lo_all, color=BLUE, marker='o', ms=3.5, label='all $n$ runs clean')
    ax.plot(n, lo_one, color=ORANGE, marker='o', ms=3.5, label='one failure in $n$')
    for k in (2, 3, 29):
        ax.plot(k, lo_all[k - 1], 'o', ms=10, mfc='none', mec=INK, mew=1.5)
    ax.text(21, 0.22, 'all clean:  2/2 ≥ {:.2f},  3/3 ≥ {:.2f},  29/29 ≥ {:.2f}'.format(
        lo_all[1], lo_all[2], lo_all[28]), fontsize=9, color=INK, bbox=dict(fc=SURF, ec=GRID))
    ax.axhline(0.9, color=MUTED, ls='--', lw=1); ax.text(1, 0.915, '0.9', color=INK2, fontsize=9)
    ax.set_xlabel('number of runs $n$'); ax.set_ylabel('95% lower bound on success rate')
    ax.set_ylim(0, 1); ax.set_xlim(0, 41); ax.legend(loc='lower right', bbox_to_anchor=(1.0, 0.3), fontsize=9)
    ax.set_title('Clopper–Pearson lower bounds (7.1): small samples bound reliability weakly')
    save(fig, 'reliability_bounds.png')


# 8.1 Friction cone vs pyramid ------------------------------------------------------------------------
def fig_cone_pyramid():
    fig, ax = plt.subplots(figsize=(5.0, 4.8))
    t = np.linspace(0, 2 * np.pi, 300)
    ax.fill(np.cos(t), np.sin(t), color=BLUE, alpha=0.12, lw=0)
    ax.plot(np.cos(t), np.sin(t), color=BLUE, lw=2.2, label=r'elliptic cone: $\|F_t\|\leq\mu N$')
    ax.plot([1, -1, -1, 1, 1], [1, 1, -1, -1, 1], color=ORANGE, lw=2.2, label=r'box pyramid: $|F_x|,|F_y|\leq\mu N$')
    arrow(ax, (0, 0), (1, 1), color=ORANGE, lw=1.6); ax.text(0.5, 0.78, r'$\sqrt{2}\,\mu N$', color=ORANGE, fontsize=11)
    arrow(ax, (0, 0), (1, 0), color=BLUE, lw=1.6); ax.text(0.45, -0.15, r'$\mu N$', color=BLUE, fontsize=11)
    ax.set_aspect('equal'); ax.set_xlim(-1.35, 1.35); ax.set_ylim(-1.35, 1.6)
    ax.set_xlabel(r'$F_x/\mu N$'); ax.set_ylabel(r'$F_y/\mu N$')
    ax.legend(loc='upper center', fontsize=8.5, ncol=1)
    ax.set_title('Tangential friction allowed at one contact')
    save(fig, 'friction_cone_pyramid.png')


# 9.2 Delaunay corridor and the follower's path ---------------------------------------------------------
def fig_delaunay():
    from scipy.spatial import Delaunay
    from saurcon_plan.cone_follower import ConeFollower
    R, w, s = 4.0, 2.2, 0.65
    # left bend starting at the car: centreline circle centred at (0, R)
    arcs = np.arange(-1.0, 7.0, s)
    th = np.clip(arcs, 0, None) / R
    cen = np.column_stack([np.where(arcs < 0, arcs, R * np.sin(th)), np.where(arcs < 0, 0, R - R * np.cos(th))])
    tang = np.column_stack([np.cos(th), np.sin(th)]); nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
    left, right = cen + w / 2 * nrm, cen - w / 2 * nrm
    rng = np.random.default_rng(4)
    keep_l = (np.hypot(*left.T) < 6.0) & (rng.random(len(left)) > 0.15)
    keep_r = (np.hypot(*right.T) < 6.5) & (rng.random(len(right)) > 0.15)
    cones = np.vstack([left[keep_l], right[keep_r]]) + rng.normal(0, 0.03, (keep_l.sum() + keep_r.sum(), 2))
    side = np.array([1] * keep_l.sum() + [-1] * keep_r.sum())
    f = ConeFollower(); f.act(cones, v=3.0)
    tri = Delaunay(cones)
    edges = set()
    for a, b, c in tri.simplices:
        edges |= {tuple(sorted(e)) for e in ((a, b), (b, c), (a, c))}
    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    for i, j in edges:
        d = math.dist(cones[i], cones[j])
        inwin = f.min_gate <= d <= f.max_gate
        same = side[i] == side[j]
        if inwin and same:
            ax.plot(*zip(cones[i], cones[j]), color=RED, lw=2.2, zorder=2)
        elif inwin:
            ax.plot(*zip(cones[i], cones[j]), color=AQUA, lw=1.2, alpha=0.9, zorder=1)
        else:
            ax.plot(*zip(cones[i], cones[j]), color=GRID, lw=1.0, zorder=0)
    ax.scatter(cones[:, 0], cones[:, 1], s=34, color=ORANGE, zorder=3, edgecolor=SURF, linewidth=0.8)
    if len(f.mids):
        ax.scatter(f.mids[:, 0], f.mids[:, 1], s=10, color=INK2, zorder=4)
    ax.plot(f.path[:, 0], f.path[:, 1], color=MAGENTA, lw=3, marker='o', ms=5, zorder=5)
    if f.target is not None:
        ax.plot(*f.target, 'o', ms=12, mfc='none', mec=RED, mew=2.2, zorder=6)
    ax.add_patch(Polygon([(0.25, 0), (-0.12, 0.12), (-0.12, -0.12)], color=INK, zorder=7))
    ax.plot([], [], color=GRID, lw=1, label='Delaunay edge, outside the length window')
    ax.plot([], [], color=AQUA, lw=1.2, label='edge in window, crossing the track (midpoint kept)')
    ax.plot([], [], color=RED, lw=2.2, label='edge in window along one boundary (rejected)')
    ax.plot([], [], color=MAGENTA, lw=3, marker='o', ms=5, label='chained path')
    ax.plot([], [], 'o', ms=10, mfc='none', mec=RED, mew=2, label='pure-pursuit target')
    ax.set_aspect('equal'); ax.set_xlabel('forward $x$ in {B} (m)'); ax.set_ylabel('left $y$ in {B} (m)')
    ax.legend(loc='upper left', fontsize=8.5)
    ax.set_title('Centreline from cones: gates 2.2 m wide, 0.65 m apart, 15% of cones missed')
    save(fig, 'delaunay_corridor.png')


# 9.3 Pure pursuit geometry ---------------------------------------------------------------------------
def fig_pure_pursuit():
    fig, ax = plt.subplots(figsize=(7.4, 5.4)); schematic(ax)
    rho, alpha = 2.4, 0.55
    ld = 2 * rho * math.sin(alpha)
    tgt = np.array([ld * math.cos(alpha), ld * math.sin(alpha)])
    th = np.linspace(-0.15, 2 * alpha + 0.25, 200)
    ax.plot(rho * np.sin(th), rho - rho * np.cos(th), color=AQUA, lw=2.2, label='arc the car will follow')
    pth = np.linspace(-0.5, 3.2, 100)
    cq = 0.05; dq = (tgt[1] - cq * tgt[0] ** 2) / tgt[0]          # path through the origin and the target
    ax.plot(pth, cq * pth ** 2 + dq * pth, color=MAGENTA, lw=2.2, ls='--', label='planned path')
    ax.plot([0, tgt[0]], [0, tgt[1]], color=INK2, lw=1.4)
    ax.plot([0, 0], [0, rho], color=MUTED, lw=1, ls='--'); ax.plot([0, tgt[0]], [rho, tgt[1]], color=MUTED, lw=1, ls='--')
    ax.plot(0, rho, 'o', color=ORANGE, ms=7); ax.text(0.08, rho + 0.08, 'centre $(0,\\rho)$', color=ORANGE, fontsize=10)
    ax.plot(*tgt, 'o', ms=12, mfc='none', mec=RED, mew=2.2); ax.text(tgt[0] + 0.1, tgt[1] - 0.05, 'target', color=RED)
    ax.add_patch(Polygon([(0.3, 0), (-0.12, 0.14), (-0.12, -0.14)], color=INK))
    arrow(ax, (0, 0), (0.9, 0), color=INK, lw=1.6)
    a = np.linspace(0, alpha, 30); ax.plot(0.7 * np.cos(a), 0.7 * np.sin(a), color=INK2, lw=1.2)
    ax.text(0.78, 0.17, r'$\alpha$', fontsize=13)
    ax.text(tgt[0] / 2 - 0.15, tgt[1] / 2 + 0.12, r'$\ell_d$', fontsize=13)
    ax.text(-0.35, rho / 2, r'$\rho$', fontsize=13)
    ax.text(-0.75, -0.5, 'rear axle {B}, heading $x$', fontsize=9, color=INK2)
    ax.text(1.7, 2.5, r'$\ell_d = 2\rho\sin\alpha$' + '\n' + r'$\kappa = 2\sin\alpha/\ell_d$' + '\n'
            + r'$\delta = \arctan(2L\sin\alpha/\ell_d)$', fontsize=11, color=INK,
            bbox=dict(fc=SURF, ec=GRID))
    ax.set_xlim(-0.8, 3.4); ax.set_ylim(-0.7, 3.4)
    ax.legend(loc='upper left', bbox_to_anchor=(0.0, -0.02), fontsize=9, ncol=2)
    save(fig, 'pure_pursuit.png')


# 4.2 Occupancy grid: log-odds along one ray ---------------------------------------------------------
def fig_occupancy():
    l0 = 0.0; lhit, lmiss = math.log(0.7 / 0.3), math.log(0.4 / 0.6)
    cells = np.arange(0, 20)
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.6), gridspec_kw={'width_ratios': [1.25, 1]})
    ax = axs[0]
    for nobs, col in ((1, MUTED), (3, ORANGE), (8, BLUE)):
        lo = np.zeros(len(cells))
        lo[:14] += nobs * lmiss; lo[14] += nobs * lhit
        p = 1 / (1 + np.exp(-lo))
        ax.step(cells, p, where='mid', color=col, lw=2, label=f'after {nobs} ray(s)')
    ax.axvline(14, color=RED, lw=1, ls=':'); ax.text(14.2, 0.05, 'depth hit', color=RED, fontsize=9)
    ax.axvspan(14.5, 19.5, color=GRID, alpha=0.5, lw=0); ax.text(15.2, 0.9, 'never reached:\nstays 0.5', fontsize=9, color=INK2)
    ax.set_xlabel('cell index along the ray'); ax.set_ylabel('$p$(occupied)'); ax.set_ylim(0, 1); ax.set_xlim(-0.5, 19.5)
    ax.legend(loc='upper left', fontsize=9)
    ax.set_title('Log-odds updates (4.3) with ProbHit 0.7, ProbMiss 0.4', fontsize=10.5)
    ax = axs[1]
    labels = ['no ray tracing', 'ray tracing\n+ footprint']
    unk = [49, 12.5]
    ax.bar(labels, unk, color=[MUTED, BLUE], width=0.5)
    ax.errorbar([1], [12.5], yerr=[[1.5], [1.5]], color=INK, capsize=5, lw=1.4)
    for i, u in enumerate(unk):
        ax.text(i, u + 4, f'{u:.0f}%' if i == 0 else '11–14%', ha='center', fontsize=10, color=INK)
    ax.set_ylabel('unknown area inside the track (%)'); ax.set_ylim(0, 60)
    ax.set_title('Feature-warehouse maps after 3–4 laps', fontsize=10.5)
    save(fig, 'occupancy.png')


if __name__ == '__main__':
    fig_ackermann(); fig_friction(); T = fig_speed_profile(); fig_ranging()
    m = fig_unscented(); fig_pose_graph(); fig_state_machine(); fig_ppo_clip(); fig_reliability()
    fig_cone_pyramid(); fig_delaunay(); fig_pure_pursuit(); fig_occupancy()
    print(f'speed-profile lap time {T:.2f} s; UT means: MC {m[0].round(3)}, linear {m[1].round(3)}, UT {m[2].round(3)}')
