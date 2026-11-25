"""A heart made from two cubic Bézier curves, one the mirror image of the other.

    python examples/heart.py          # writes heart.png

Shapes in fonts and vector graphics are chains of curves like these. Mirroring the
control points mirrors the curve, because a Bézier curve is built only from its points.
"""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

RIGHT = np.array([[0.0, -1.0], [1.55, 0.15], [0.75, 1.25], [0.0, 0.55]])
LEFT = RIGHT * [-1, 1]


def main(out_dir=".") -> Path:
    """Draw the heart with its control polygons and save heart.png."""
    fig = Figure(figsize=(5, 5), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    outline = np.vstack([bv.points(RIGHT, n=200), bv.points(LEFT, n=200)[::-1]])
    ax.fill(*outline.T, color="#e0245e", alpha=0.9, lw=0)
    for ctrl in (RIGHT, LEFT):
        ax.plot(*ctrl.T, "--", color="0.45", lw=1)
        ax.plot(*ctrl[1:3].T, "o", color="#1f8f7e", ms=7)
    ax.plot(*RIGHT[[0, 3]].T, "s", color="0.15", ms=7)
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-1.3, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")
    out = Path(out_dir) / "heart.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
