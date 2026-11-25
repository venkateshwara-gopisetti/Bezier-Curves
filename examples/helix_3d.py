"""A 3-D spring built from cubic Bézier curves. Every function except animate() works in 3-D.

    python examples/helix_3d.py    # writes helix_3d.png

A quarter circle is very nearly a cubic Bézier curve whose handles have length
k = 4/3 * (sqrt(2) - 1) ≈ 0.5523 times the radius, which is how vector graphics
draw circles. Giving each quarter a rise in z turns the chain into a helix.
arc_length() then measures the spring, and the result is compared with the exact
helix length.
"""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

TURNS, RISE = 3, 1.0                       # number of turns; height gained per turn
K = 4 / 3 * (np.sqrt(2) - 1)


def quarter_turns():
    """Cubic segments, shape (4 * TURNS, 4, 3), each tracing a quarter turn of the helix."""
    segments = []
    for q in range(4 * TURNS):
        a0, a1 = q * np.pi / 2, (q + 1) * np.pi / 2
        z0, z1 = q * RISE / 4, (q + 1) * RISE / 4
        p0 = np.array([np.cos(a0), np.sin(a0), z0])
        p3 = np.array([np.cos(a1), np.sin(a1), z1])
        # Handles: K along the circle's tangent, and a third of the rise in z.
        t0 = np.array([-np.sin(a0) * K, np.cos(a0) * K, (z1 - z0) / 3])
        t1 = np.array([-np.sin(a1) * K, np.cos(a1) * K, (z1 - z0) / 3])
        segments.append([p0, p0 + t0, p3 - t1, p3])
    return np.array(segments)


def main(out_dir=".") -> Path:
    """Draw the spring with its control points; save helix_3d.png."""
    segments = quarter_turns()
    curves = bv.points_batch(segments, n=40)               # (segments, 40, 3)
    length = sum(bv.arc_length(seg) for seg in segments)
    exact = TURNS * np.hypot(2 * np.pi, RISE)

    fig = Figure(figsize=(5, 5.4), dpi=100, facecolor="white")
    ax = fig.add_subplot(projection="3d")
    for seg in segments:
        ax.plot(*seg.T, "-", color="#21918c", lw=0.8, alpha=0.6)
        ax.plot(*seg[1:3].T, "o", color="#21918c", ms=3)
        ax.plot(*seg[[0]].T, "s", color="#e0245e", ms=4)
    for curve in curves:
        ax.plot(*curve.T, color="black", lw=2.2)
    ax.set_title(f"{len(segments)} cubic segments\nlength {length:.4f} (exact helix {exact:.4f})",
                 fontsize=11)
    ax.set_box_aspect((1, 1, 1.4))
    ax.view_init(elev=16, azim=-60)
    ax.set_axis_off()
    out = Path(out_dir) / "helix_3d.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
