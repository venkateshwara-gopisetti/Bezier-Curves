"""Degree elevation: the same curve, described by more and more control points.

    python examples/degree_elevation.py    # writes degree_elevation.png

elevate() adds control points without changing the curve at all. As the degree
grows, the control polygon closes in on the curve itself.
"""

from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

CTRL = np.array([[0, 0], [2, 7], [8, 8], [10, 1]], dtype=float)
TIMES = (0, 1, 3, 8, 30)


def main(out_dir=".") -> Path:
    """Overlay the control polygons after 0, 1, 3, 8 and 30 elevations; save the PNG."""
    fig = Figure(figsize=(5, 4.2), dpi=100, facecolor="white")
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    cmap = matplotlib.colormaps["viridis"]
    for i, times in enumerate(TIMES):
        poly = bv.elevate(CTRL, times)
        ax.plot(*poly.T, "-o", color=cmap(0.9 * i / (len(TIMES) - 1)), lw=1.3, ms=3,
                label=f"degree {len(poly) - 1}")
    ax.plot(*bv.points(CTRL, n=300).T, color="black", lw=2.4, label="the curve")
    ax.legend(frameon=False, loc="lower center", fontsize=9)
    ax.set_aspect("equal")
    ax.axis("off")
    out = Path(out_dir) / "degree_elevation.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
