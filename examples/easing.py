"""CSS easing curves: every `cubic-bezier(x1, y1, x2, y2)` in a stylesheet is a Bézier curve.

    python examples/easing.py    # writes easing.png

The curve runs from (0, 0) to (1, 1); x is time and y is progress. To find the
progress at a given time, sample the curve densely and interpolate y at that x.
The dots on the right of each panel show where an animated element would be at
ten equal steps in time.
"""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

import beziervis as bv

EASINGS = {
    "ease": (0.25, 0.1, 0.25, 1.0),
    "ease-in": (0.42, 0.0, 1.0, 1.0),
    "ease-out": (0.0, 0.0, 0.58, 1.0),
    "ease-in-out": (0.42, 0.0, 0.58, 1.0),
    "back (overshoot)": (0.68, -0.6, 0.32, 1.6),
}


def progress(x1, y1, x2, y2, time):
    """Progress at each value of `time` for the CSS cubic-bezier(x1, y1, x2, y2)."""
    curve = bv.points([[0, 0], [x1, y1], [x2, y2], [1, 1]], n=1000)
    return np.interp(time, curve[:, 0], curve[:, 1])


def main(out_dir=".") -> Path:
    """Draw the five easings with their control handles; save easing.png."""
    fig = Figure(figsize=(10, 4.4), dpi=100, facecolor="white")
    axes = fig.subplots(1, len(EASINGS))
    for ax, (name, (x1, y1, x2, y2)) in zip(axes, EASINGS.items()):
        ctrl = np.array([[0, 0], [x1, y1], [x2, y2], [1, 1]])
        ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="0.9", lw=1)
        ax.plot(*ctrl[:2].T, "-o", color="#1f8f7e", lw=1, ms=4)
        ax.plot(*ctrl[2:].T, "-o", color="#1f8f7e", lw=1, ms=4)
        ax.plot(*bv.points(ctrl, n=200).T, color="black", lw=2.2)
        steps = progress(x1, y1, x2, y2, np.linspace(0, 1, 11))
        ax.plot(np.full_like(steps, 1.18), steps, "o", color="#e0245e", ms=4)
        ax.set_title(name, fontsize=12, family="monospace")
        ax.set_xlim(-0.08, 1.28)
        ax.set_ylim(-0.7, 1.7)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.tight_layout()
    out = Path(out_dir) / "easing.png"
    fig.savefig(out)
    return out


if __name__ == "__main__":
    print(main())
