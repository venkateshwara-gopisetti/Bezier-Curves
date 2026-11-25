"""Regenerate the images in docs/assets/.

    python docs/make_assets.py
"""

from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

import beziervis as bv

ASSETS = Path(__file__).parent / "assets"
HERO = [[-80, -60], [-60, 70], [10, 90], [70, 40], [85, -70]]
CUBIC = [[0, 0], [5, 10], [9, 7], [4, 3]]


def draw_construction(ax, ctrl, t, labels=True):
    """Draw every de Casteljau level at parameter t plus the curve up to t."""
    steps = bv.casteljau_steps(ctrl, t)
    cmap = matplotlib.colormaps["viridis"]
    n = len(steps)
    for level, pts in enumerate(steps[:-1]):
        color = cmap(0.9 * level / max(n - 2, 1))
        ax.add_collection(LineCollection(np.stack([pts[:-1], pts[1:]], 1), colors=[color], lw=1.6))
        ax.plot(*pts.T, "o", ms=4, color=color)
        if labels:
            for i, p in enumerate(pts):
                ax.annotate(f"{chr(65 + level)}{i}", p, xytext=(4, 4),
                            textcoords="offset points", fontsize=8, color="0.25")
    full = bv.points(ctrl, n=300)
    ax.plot(*full.T, color="0.8", lw=1.5, ls="--")
    ax.plot(*bv.points(ctrl, t=np.linspace(0, t, 200)).T, color="black", lw=2.2)
    ax.plot(*steps[-1].T, "o", color="crimson", ms=7)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def how_it_works():
    """Four panels: the same cubic at t = 0.2, 0.4, 0.6, 0.8."""
    fig = Figure(figsize=(12, 3.4), dpi=100)
    axes = fig.subplots(1, 4)
    for ax, t in zip(axes, (0.2, 0.4, 0.6, 0.8)):
        draw_construction(ax, np.array(CUBIC, float), t)
        ax.set_title(f"t = {t}", fontsize=12)
        ax.set_xlim(-1, 10.5)
        ax.set_ylim(-1, 11)
    fig.tight_layout()
    fig.savefig(ASSETS / "how-it-works.png", facecolor="white")


def social_preview():
    """1280x640 image for the GitHub social preview."""
    fig = Figure(figsize=(12.8, 6.4), dpi=100, facecolor="white")
    ax = fig.add_axes([0.52, 0.06, 0.45, 0.88])
    draw_construction(ax, np.array(HERO, float), 0.55, labels=False)
    fig.text(0.06, 0.60, "beziervis", fontsize=64, weight="bold", family="monospace")
    fig.text(0.06, 0.47, "Watch a Bézier curve build itself.", fontsize=22, color="0.25")
    fig.text(0.06, 0.36, "Fast NumPy core · optional Numba · GIFs in one line",
             fontsize=15, color="0.4")
    fig.text(0.06, 0.18, "pip install beziervis", fontsize=18, family="monospace",
             color="white", bbox={"boxstyle": "round,pad=0.5", "fc": "0.15", "ec": "none"})
    fig.savefig(ASSETS / "social-preview.png", facecolor="white")


def main():
    """Write every asset and print the file sizes."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    bv.animate(HERO, frames=90, verbose=True, fps=30, hold=45, size=480).save(
        str(ASSETS / "hero.gif"))
    bv.animate(CUBIC, frames=60, fps=30, hold=30, size=360).save(str(ASSETS / "simple.gif"))
    how_it_works()
    social_preview()
    for path in sorted(ASSETS.iterdir()):
        print(f"{path.name:22} {path.stat().st_size / 1024:8.0f} KiB")


if __name__ == "__main__":
    main()
