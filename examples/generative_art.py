"""Generative art: three thousand cubic curves, evaluated in one call to points_batch().

    python examples/generative_art.py    # writes generative_art.png

Every curve leaves a small inner circle and lands on an outer one a little further
round, with randomly jittered handles. points_batch() evaluates all of them at once
as an array of shape (curves, points, 2).
"""

import time
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

import beziervis as bv

N_CURVES = 3000


def make_curves(n, seed=7):
    """n cubic curves swirling outward from a ring, as an array of shape (n, 4, 2)."""
    rng = np.random.default_rng(seed)
    a = rng.uniform(0, 2 * np.pi, n)
    twist = 1.3 + 0.4 * np.sin(5 * a)

    def ring(radius, angle):
        return np.stack([radius * np.cos(angle), radius * np.sin(angle)], axis=-1)

    curves = np.stack([
        ring(0.35, a),
        ring(1.4, a + 0.5 * twist) + rng.normal(0, 0.12, (n, 2)),
        ring(2.2, a + 1.1 * twist) + rng.normal(0, 0.12, (n, 2)),
        ring(2.6 + 0.25 * np.sin(5 * a), a + 1.6 * twist),
    ], axis=1)
    return curves, a


def main(out_dir=".") -> Path:
    """Evaluate the curves in one batch and draw them; save generative_art.png."""
    curves, angle = make_curves(N_CURVES)
    bv.points_batch(curves[:2], n=80)          # warm-up: Numba compiles on the first call
    start = time.perf_counter()
    pts = bv.points_batch(curves, n=80)
    elapsed = time.perf_counter() - start
    print(f"{N_CURVES} curves x 80 points evaluated in {elapsed * 1e3:.1f} ms ({bv.get_backend()})")

    fig = Figure(figsize=(5, 5), dpi=120, facecolor="#0e1014")
    ax = fig.add_axes([0, 0, 1, 1])
    colors = matplotlib.colormaps["viridis"]((np.sin(3 * angle) + 1) / 2)
    ax.add_collection(LineCollection(pts, colors=colors, lw=0.35, alpha=0.35))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect("equal")
    ax.axis("off")
    out = Path(out_dir) / "generative_art.png"
    fig.savefig(out, facecolor=fig.get_facecolor())
    return out


if __name__ == "__main__":
    print(main())
