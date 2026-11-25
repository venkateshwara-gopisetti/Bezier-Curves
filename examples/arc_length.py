"""Even spacing along a curve: equal steps in t are not equal steps in distance.

    python examples/arc_length.py    # writes arc_length.png

Points at evenly spaced t bunch up where the curve moves slowly. To space them
evenly by distance, measure the length s(t) from the start to each t (the left half
from split() has exactly that length), then invert s(t) by interpolation.
"""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

# Three control points stacked on one spot make the curve crawl past it and race elsewhere.
CTRL = np.array([[0, 0], [2, 6], [5, 3], [5, 3], [5, 3], [8, 0], [10, 6]], dtype=float)
N = 21


def even_t(ctrl, n, samples=200):
    """Parameters t at which the curve is divided into n-1 pieces of equal length."""
    grid = np.linspace(0, 1, samples)
    s = np.array([0.0] + [bv.arc_length(bv.split(ctrl, t)[0]) for t in grid[1:]])
    return np.interp(np.linspace(0, s[-1], n), s, grid)


def main(out_dir=".") -> Path:
    """Compare evenly spaced t with evenly spaced distance; save arc_length.png."""
    curve = bv.points(CTRL, n=300)
    fig = Figure(figsize=(10, 3.6), dpi=100, facecolor="white")
    axes = fig.subplots(1, 2)
    panels = [("equal steps in t", np.linspace(0, 1, N)),
              (f"equal steps in length ({bv.arc_length(CTRL):.2f} in total)", even_t(CTRL, N))]
    for ax, (title, t) in zip(axes, panels):
        ax.plot(*CTRL.T, "--", color="0.8", lw=1)
        ax.plot(*curve.T, color="black", lw=2)
        ax.plot(*bv.points(CTRL, t=t).T, "o", color="#e0245e", ms=6, zorder=3)
        ax.set_title(title, fontsize=12)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    out = Path(out_dir) / "arc_length.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
