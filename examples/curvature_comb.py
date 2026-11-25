"""A curvature comb, the tool CAD programs use to judge how smooth a curve is.

    python examples/curvature_comb.py    # writes curvature_comb.png

Each tooth points along the normal, with a length proportional to the curvature

    k(t) = (x' y'' - y' x'') / |B'(t)|^3

Both derivatives come from derivative(), which returns the control points of the
derivative curve: itself a Bézier curve, one degree lower.
"""

from pathlib import Path

import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

import beziervis as bv

CTRL = np.array([[0, 0], [1.5, 2.6], [3.2, -1.6], [4.6, 2.4], [6.4, 0.4], [7.2, 1.6]])
SCALE = 0.35


def curvature(ctrl, t):
    """Signed curvature and unit normal of the curve at parameters t."""
    d1 = bv.points(bv.derivative(ctrl), t=t)
    d2 = bv.points(bv.derivative(bv.derivative(ctrl)), t=t)
    speed = np.linalg.norm(d1, axis=1)
    k = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / speed**3
    normal = np.column_stack([-d1[:, 1], d1[:, 0]]) / speed[:, None]
    return k, normal


def main(out_dir=".") -> Path:
    """Draw the curve with its comb and save curvature_comb.png."""
    t = np.linspace(0, 1, 160)
    curve = bv.points(CTRL, t=t)
    k, normal = curvature(CTRL, t)
    tips = curve - SCALE * k[:, None] * normal

    fig = Figure(figsize=(7, 3.6), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.plot(*CTRL.T, "--o", color="0.75", lw=1, ms=4)
    ax.add_collection(LineCollection(np.stack([curve, tips], axis=1), colors="#5ec962", lw=0.8))
    ax.plot(*tips.T, color="#21918c", lw=1.4)
    ax.plot(*curve.T, color="black", lw=2.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.04)
    out = Path(out_dir) / "curvature_comb.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
