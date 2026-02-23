"""
FREE1105 - Phase 4: Geometrical Curvature Visualiser
=====================================================
Renders the electric potential V(x,y) = sum(kq/r) as a 3D surface
in a separate matplotlib window.

- Positive potential regions: warped UPWARD, coloured towards white (matching existing field)
- Negative potential regions: warped DOWNWARD, coloured towards dark/black
- Blue wireframe overlaid on coloured surface
- Updates 5 times per second via a background thread

USAGE:
    Import and instantiate Phase4Visualiser, then call:
        vis.update(all_point_charges)   <- call this every frame from your main loop
        vis.start()                     <- call once after pygame init
        vis.stop()                      <- call on exit

INTEGRATION (drop into your main.py):
    from phase4_visualiser import Phase4Visualiser
    phase4 = Phase4Visualiser()
    phase4.start()

    # Inside your main loop render section:
    phase4.update(all_point_charges)

    # On exit (after pygame.quit()):
    phase4.stop()
"""

import threading
import time
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Must be set before importing pyplot
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize

# ── constants (mirrored from constants_for_all_files.py) ──────────────────────
K_COULOMB = 8.99e9
SW = 1500
SH = 900

# Grid resolution for the 3D surface (higher = prettier but slower)
GRID_RES = 60          # NxN grid points
UPDATE_INTERVAL = 0.2  # seconds between redraws (= 5 Hz)


def _compute_potential(charges, grid_x, grid_y):
    """
    Vectorised V(x,y) = sum_i  k * q_i / r_i
    Returns a (GRID_RES, GRID_RES) float array.
    """
    V = np.zeros_like(grid_x, dtype=float)
    for pc in charges:
        px, py = pc.position[0], pc.position[1]
        dx = grid_x - px
        dy = grid_y - py
        r = np.sqrt(dx**2 + dy**2)
        # soften to avoid singularity (use particle radius as floor)
        r_min = getattr(pc, 'total_radius', 20.0)
        r = np.maximum(r, r_min)
        V += K_COULOMB * pc.charge / r
    return V


def _make_surface_colors(V_norm):
    """
    Map normalised potential [-1, 1] to RGBA colours.
    Positive (white-ish) matches the existing field heatmap light region.
    Negative (dark/near-black) matches the dark region.
    The neutral midpoint is mid-grey (128, 128, 128) — same as BGC.

    V_norm: array in [-1, 1]
    Returns RGBA array shape (*V_norm.shape, 4)
    """
    # pixel_val formula mirrors electric_field.py:
    #   pixel_vals = 127.5 - (0.7 * normalised * 127.5)
    # but we extend it to full [-1,1] range here for better visual pop
    pixel_vals = 0.5 - (0.5 * V_norm)   # in [0, 1], 0=dark, 1=bright

    # Build RGB: grey scale (same as the 2D heatmap — all channels equal)
    r = pixel_vals
    g = pixel_vals
    b = pixel_vals
    a = np.ones_like(r) * 0.85   # slight transparency so wireframe pops

    return np.stack([r, g, b, a], axis=-1)


class Phase4Visualiser:
    """
    Manages a separate matplotlib 3D window that shows the electric potential
    surface, updated at ~5 Hz from a background thread.
    """

    def __init__(self, grid_res=GRID_RES, update_interval=UPDATE_INTERVAL):
        self.grid_res = grid_res
        self.update_interval = update_interval

        # Shared state between main thread (writes charges) and bg thread (reads)
        self._lock = threading.Lock()
        self._charges_snapshot = []   # list of (px, py, charge, radius) tuples
        self._running = False
        self._thread = None

        # Build grid in world-space (pixels)
        xs = np.linspace(0, SW, grid_res)
        ys = np.linspace(0, SH, grid_res)
        self._grid_x, self._grid_y = np.meshgrid(xs, ys)

        # Normalised grid in [0,1] for axis display
        self._gx_norm = self._grid_x / SW
        self._gy_norm = self._grid_y / SH

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self):
        """Spawn the background rendering thread and open the matplotlib window."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._render_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Signal the background thread to stop."""
        self._running = False

    def update(self, all_point_charges):
        """
        Call this every frame from your main loop.
        Stores a lightweight snapshot of charge data (thread-safe).
        """
        snapshot = []
        for pc in all_point_charges:
            snapshot.append({
                'px': float(pc.position[0]),
                'py': float(pc.position[1]),
                'charge': float(pc.charge),
                'radius': float(getattr(pc, 'total_radius', 20.0)),
            })
        with self._lock:
            self._charges_snapshot = snapshot

    # ── Background render loop ────────────────────────────────────────────────

    def _render_loop(self):
        """Runs in background thread. Creates and continuously updates the 3D plot."""
        plt.ion()
        fig = plt.figure(figsize=(8, 6), facecolor='#1a1a2e')
        fig.canvas.manager.set_window_title("FREE1105 — Phase 4: Potential Surface")
        ax = fig.add_subplot(111, projection='3d')
        self._style_axes(ax)

        last_update = 0.0

        while self._running:
            now = time.time()
            if now - last_update < self.update_interval:
                plt.pause(0.02)
                continue

            last_update = now

            # Grab snapshot
            with self._lock:
                charges = list(self._charges_snapshot)

            ax.cla()
            self._style_axes(ax)

            if not charges:
                ax.set_title("No charges present", color='white', fontsize=12, pad=15)
                plt.draw()
                plt.pause(0.02)
                continue

            # ── Compute potential ─────────────────────────────────────────
            V = np.zeros_like(self._grid_x, dtype=float)
            for c in charges:
                dx = self._grid_x - c['px']
                dy = self._grid_y - c['py']
                r = np.sqrt(dx**2 + dy**2)
                r = np.maximum(r, c['radius'])
                V += K_COULOMB * c['charge'] / r

            # ── Normalise for colour and z-height ─────────────────────────
            v_abs_max = np.max(np.abs(V))
            if v_abs_max == 0:
                v_abs_max = 1.0
            V_norm = np.clip(V / v_abs_max, -1.0, 1.0)   # [-1, 1]

            # Z: positive up, negative down — scale to visual range
            Z = V_norm * 0.4   # [-0.4, 0.4] in normalised coords

            # ── Face colours (grey scale matching 2D heatmap) ─────────────
            face_colors = _make_surface_colors(V_norm)

            # ── Draw solid surface ────────────────────────────────────────
            ax.plot_surface(
                self._gx_norm, self._gy_norm, Z,
                facecolors=face_colors,
                shade=False,
                antialiased=False,
                zorder=1,
            )

            # ── Draw wireframe on top ─────────────────────────────────────
            ax.plot_wireframe(
                self._gx_norm, self._gy_norm, Z,
                color='#00aaff',      # electric blue, matches your aesthetic
                linewidth=0.5,
                alpha=0.55,
                zorder=2,
            )

            # ── Mark charge positions ──────────────────────────────────────
            for c in charges:
                cx_n = c['px'] / SW
                cy_n = c['py'] / SH
                # Interpolate z at charge position (nearest grid point)
                ix = int(np.clip(cx_n * (self.grid_res - 1), 0, self.grid_res - 1))
                iy = int(np.clip(cy_n * (self.grid_res - 1), 0, self.grid_res - 1))
                cz = Z[iy, ix]

                colour = '#ff3333' if c['charge'] > 0 else '#3333ff' if c['charge'] < 0 else '#888888'
                ax.scatter(
                    [cx_n], [cy_n], [cz + 0.03],
                    color=colour,
                    s=80,
                    zorder=5,
                    depthshade=False,
                )

            # ── Title with charge count ───────────────────────────────────
            n_pos = sum(1 for c in charges if c['charge'] > 0)
            n_neg = sum(1 for c in charges if c['charge'] < 0)
            ax.set_title(
                f"Electric Potential  |  +{n_pos} positive   −{n_neg} negative",
                color='white', fontsize=11, pad=12
            )

            plt.draw()
            plt.pause(0.02)

        plt.close('all')

    # ── Axis styling helper ───────────────────────────────────────────────────

    @staticmethod
    def _style_axes(ax):
        ax.set_facecolor('#1a1a2e')
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('#333355')
        ax.yaxis.pane.set_edgecolor('#333355')
        ax.zaxis.pane.set_edgecolor('#333355')
        ax.tick_params(colors='#aaaacc', labelsize=7)
        ax.set_xlabel("X", color='#aaaacc', fontsize=8, labelpad=4)
        ax.set_ylabel("Y", color='#aaaacc', fontsize=8, labelpad=4)
        ax.set_zlabel("V (norm)", color='#aaaacc', fontsize=8, labelpad=4)
        ax.set_zlim(-0.5, 0.5)
        ax.grid(False)