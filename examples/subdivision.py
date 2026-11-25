"""Recursive subdivision: split a curve in half, again and again.

    python examples/subdivision.py    # writes subdivision.png

split() cuts a curve into two curves of the same degree that together trace exactly
the original. Their control polygons hug the curve more closely each round, which is
how renderers and intersection tests turn curves into straight lines.
"""

from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

CTRL = np.array([[-80, -60], [-60, 70], [10, 90], [70, 40], [85, -70]], dtype=float)
DEPTHS = (0, 1, 2, 4)


def subdivide(ctrl, depth):
    """Return the 2**depth pieces of ctrl after `depth` rounds of halving."""
    pieces = [ctrl]
    for _ in range(depth):
        pieces = [half for piece in pieces for half in bv.split(piece, 0.5)]
    return pieces


def main(out_dir=".") -> Path:
    """Draw four rounds of subdivision side by side and save subdivision.png."""
    fig = Figure(figsize=(10, 2.9), dpi=100, facecolor="white")
    axes = fig.subplots(1, len(DEPTHS))
    cmap = matplotlib.colormaps["viridis"]
    curve = bv.points(CTRL, n=300)
    for ax, depth in zip(axes, DEPTHS):
        pieces = subdivide(CTRL, depth)
        ax.plot(*curve.T, color="black", lw=2.2, zorder=3)
        for i, piece in enumerate(pieces):
            color = cmap(0.85 * i / max(len(pieces) - 1, 1))
            ax.plot(*piece.T, "-o", color=color, lw=1.1, ms=2.5)
        ax.set_title(f"{len(pieces)} piece{'s' if len(pieces) > 1 else ''}", fontsize=12)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    out = Path(out_dir) / "subdivision.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
