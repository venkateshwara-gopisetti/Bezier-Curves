"""A calligraphic "S": cubic Bézier segments stroked with a broad-nib pen.

    python examples/calligraphy.py    # writes calligraphy.png

The path is four cubic segments joined smoothly: at each join the handles on both
sides lie on one line, so the tangent does not jump. A broad nib held at a fixed
angle makes the stroke thick where the path moves across the nib and thin where it
moves along it, which is how pen lettering gets its contrast.
"""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

SEGMENTS = np.array([
    [[1.0, 1.75], [0.6, 2.15], [-0.9, 2.1], [-0.8, 1.45]],
    [[-0.8, 1.45], [-0.7, 0.85], [0.9, 1.0], [0.85, 0.35]],
    [[0.85, 0.35], [0.8, -0.3], [-0.6, -0.35], [-1.0, 0.1]],
    [[-1.0, 0.1], [-1.4, 0.55], [-1.6, -0.6], [1.5, -0.45]],
])
NIB_ANGLE = np.radians(35)
NIB_WIDTH = 0.22


def main(out_dir=".") -> Path:
    """Stroke the path with a broad nib and save calligraphy.png."""
    fig = Figure(figsize=(5, 5), dpi=100, facecolor="#fbf8f1")
    ax = fig.add_axes([0, 0, 1, 1])
    nib = NIB_WIDTH / 2 * np.array([np.cos(NIB_ANGLE), np.sin(NIB_ANGLE)])
    for seg in SEGMENTS:
        path = bv.points(seg, n=300)
        # The nib sweeps a quadrilateral between every pair of neighbouring points.
        for a, b in zip(path[:-1], path[1:]):
            quad = np.array([a + nib, b + nib, b - nib, a - nib])
            ax.fill(*quad.T, color="#1b1d22", lw=0.6, ec="#1b1d22")
    for seg in SEGMENTS:
        ax.plot(*seg[:2].T, "-", color="#1f8f7e", lw=1)
        ax.plot(*seg[2:].T, "-", color="#1f8f7e", lw=1)
        ax.plot(*seg[1:3].T, "o", color="#1f8f7e", ms=4)
        ax.plot(*seg[[0, 3]].T, "s", color="#e0245e", ms=5)
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-1.1, 2.5)
    ax.set_aspect("equal")
    ax.axis("off")
    out = Path(out_dir) / "calligraphy.png"
    fig.savefig(out, facecolor=fig.get_facecolor())
    return out


if __name__ == "__main__":
    print(main())
