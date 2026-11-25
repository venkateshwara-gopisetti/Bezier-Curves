"""Animate de Casteljau's construction of a 2-D Bézier curve (needs matplotlib).

>>> import beziervis as bv
>>> anim = bv.animate([[0, 0], [5, 10], [9, 7], [4, 3]], verbose=True)
>>> anim.save("curve.gif")       # doctest: +SKIP
>>> anim.show()                  # doctest: +SKIP

In Jupyter, an animation that is the last expression in a cell is displayed
inline as an interactive player.

``save`` and the Jupyter display draw on a plain
:class:`matplotlib.figure.Figure`, not through pyplot, so they work on
machines without a display. Only :meth:`BezierAnimation.show` uses pyplot.
"""

from __future__ import annotations

import os
from typing import Optional

import numpy as np

try:
    import matplotlib
    from matplotlib import animation as mpl_animation
    from matplotlib.collections import LineCollection
    from matplotlib.figure import Figure
except ImportError as exc:  # pragma: no cover - exercised only without matplotlib
    raise ImportError(
        "beziervis.animation needs matplotlib; install it with: pip install beziervis[anim]"
    ) from exc

from .core import ArrayLike, as_control_points, casteljau_steps, points

#: Above this many control points, point labels are off by default.
MAX_DEFAULT_LABELS = 10


def _level_colors(n_ctrl: int, cmap_name: str) -> list:
    """Split one colormap across every segment of every construction level.

    Level 0 (the control polygon) has ``n_ctrl - 1`` segments, level 1 has
    ``n_ctrl - 2`` and so on, so each segment gets its own colour and the
    levels read as a gradient.
    """
    n_segments = max(1, n_ctrl * (n_ctrl - 1) // 2)
    palette = matplotlib.colormaps[cmap_name](np.linspace(0, 0.9, n_segments))
    colors, start = [], 0
    for level in range(n_ctrl):
        count = n_ctrl - 1 - level
        colors.append(palette[start:start + count])
        start += count
    return colors


def _label_prefix(level: int) -> str:
    """Return the label letter for a construction level: A, B, ..., Z, L26, L27, ..."""
    return chr(ord("A") + level) if level < 26 else f"L{level}"


class BezierAnimation:  # pylint: disable=too-many-instance-attributes
    """An animation of a 2-D Bézier curve being traced by de Casteljau's algorithm.

    Parameters
    ----------
    ctrl : array_like, shape (k, 2)
        Control points.
    frames : int, default 100
        Number of parameter values between 0 and 1, i.e. animation steps.
    verbose : bool, default False
        Also draw the intermediate construction lines at every level. Best
        kept for curves with about 6 control points or fewer.
    labels : bool, optional
        Label each point (A0, A1, ... for control points; B0, ... for level 1).
        Defaults to True for up to 10 control points.
    fps : int, default 30
        Playback speed.
    hold : int, default 30
        Extra frames that hold the finished curve before the animation loops.
    size : int, default 600
        Width and height of the figure in pixels.
    cmap : str, default "viridis"
        Matplotlib colormap for the construction lines.
    title : str, optional
        Figure title. Defaults to "Bézier curve (degree N)".
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        ctrl: ArrayLike,
        frames: int = 100,
        verbose: bool = False,
        labels: Optional[bool] = None,
        *,
        fps: int = 30,
        hold: int = 30,
        size: int = 600,
        cmap: str = "viridis",
        title: Optional[str] = None,
    ):
        self.ctrl = as_control_points(ctrl)
        if self.ctrl.shape[1] != 2:
            raise ValueError(
                f"animate() draws 2-D curves; got {self.ctrl.shape[1]}-D control points"
            )
        if frames < 2:
            raise ValueError(f"frames must be at least 2; got {frames}")
        if fps < 1 or hold < 0 or size < 50:
            raise ValueError("need fps >= 1, hold >= 0 and size >= 50")
        self.frames = int(frames)
        self.verbose = bool(verbose)
        self.labels = (
            len(self.ctrl) <= MAX_DEFAULT_LABELS if labels is None else bool(labels)
        )
        self.fps = int(fps)
        self.hold = int(hold)
        self.size = int(size)
        self.cmap = cmap
        self.title = title or f"Bézier curve (degree {len(self.ctrl) - 1})"
        self.t = np.linspace(0.0, 1.0, self.frames)
        self.curve = points(self.ctrl, t=self.t)
        self.animation: Optional[mpl_animation.FuncAnimation] = None

    # ------------------------------------------------------------------ building

    def _limits(self):
        """Square limits around the control points (the curve stays inside their hull)."""
        lo, hi = self.ctrl.min(axis=0), self.ctrl.max(axis=0)
        center = (lo + hi) / 2
        half = float(np.max(hi - lo)) / 2 * 1.12
        if half < 1e-9:  # all control points coincide
            half = 1.0
        return (center[0] - half, center[0] + half), (center[1] - half, center[1] + half)

    def _draw_level(self, ax, pts, colors, level, zorder):
        """Draw one construction level; return its (lines, markers, texts)."""
        lines = LineCollection(
            np.stack([pts[:-1], pts[1:]], axis=1), colors=colors, linewidths=1.5,
            alpha=0.8, zorder=zorder,
        )
        ax.add_collection(lines)
        marker_color = colors[0] if len(colors) else "0.3"
        (markers,) = ax.plot(*pts.T, "o", ms=4, color=marker_color, zorder=zorder + 0.1)
        texts = []
        if self.labels:
            prefix = _label_prefix(level)
            texts = [
                ax.annotate(f"{prefix}{i}", p, xytext=(4, 4), textcoords="offset points",
                            fontsize=9, color="0.2", zorder=zorder + 0.2)
                for i, p in enumerate(pts)
            ]
        return lines, markers, texts

    def _build(self, fig) -> mpl_animation.FuncAnimation:  # pylint: disable=too-many-locals
        ax = fig.add_subplot()
        fig.suptitle(self.title, fontsize=16)
        xlim, ylim = self._limits()
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.25)

        n_ctrl = len(self.ctrl)
        colors = _level_colors(n_ctrl, self.cmap)
        self._draw_level(ax, self.ctrl, colors[0], 0, zorder=2)

        # Intermediate levels 1 .. k-2 (level k-1 is the single traced point).
        dynamic = []
        if self.verbose:
            steps = casteljau_steps(self.ctrl, 0.0)
            for level in range(1, n_ctrl - 1):
                dynamic.append(self._draw_level(ax, steps[level], colors[level], level, 3))

        (trace,) = ax.plot([], [], color="black", lw=2, label="Bézier curve", zorder=4)
        (head,) = ax.plot([], [], "o", color="crimson", ms=7, zorder=5)
        ax.legend(loc="upper right")

        last = self.frames - 1

        def update(frame):
            i = min(frame, last)
            trace.set_data(self.curve[: i + 1, 0], self.curve[: i + 1, 1])
            head.set_data(self.curve[i : i + 1, 0], self.curve[i : i + 1, 1])
            if dynamic:
                steps = casteljau_steps(self.ctrl, self.t[i])
                visible = i < last  # at t = 1 every level collapses onto the end point
                for level, (lines, markers, texts) in enumerate(dynamic, start=1):
                    pts = steps[level]
                    lines.set_segments(np.stack([pts[:-1], pts[1:]], axis=1))
                    markers.set_data(pts[:, 0], pts[:, 1])
                    for text, p in zip(texts, pts):
                        text.xy = p
                    for artist in (lines, markers, *texts):
                        artist.set_visible(visible)
            return []

        update(0)
        return mpl_animation.FuncAnimation(
            fig, update, frames=self.frames + self.hold, interval=1000 / self.fps,
            blit=False, repeat=True, cache_frame_data=False,
        )

    def _offscreen(self) -> mpl_animation.FuncAnimation:
        fig = Figure(figsize=(self.size / 100, self.size / 100), dpi=100)
        self.animation = self._build(fig)
        return self.animation

    # ------------------------------------------------------------------ output

    def save(self, path: str, dpi: int = 100) -> str:
        """Save as ``.gif`` (Pillow) or ``.mp4`` (needs ffmpeg). Returns ``path``."""
        ext = os.path.splitext(path)[1].lower()
        if ext == ".gif":
            writer = mpl_animation.PillowWriter(fps=self.fps)
        elif ext == ".mp4":
            if not mpl_animation.writers.is_available("ffmpeg"):
                raise RuntimeError("saving .mp4 needs ffmpeg on PATH; save a .gif instead")
            writer = mpl_animation.FFMpegWriter(fps=self.fps)
        else:
            raise ValueError(f"unsupported file type {ext!r}; use .gif or .mp4")
        self._offscreen().save(path, writer=writer, dpi=dpi)
        return path

    def to_jshtml(self) -> str:
        """Return the animation as a self-contained HTML/JavaScript player."""
        return self._offscreen().to_jshtml(fps=self.fps)

    def _repr_html_(self) -> str:
        return self.to_jshtml()

    def show(self) -> "BezierAnimation":
        """Open the animation in an interactive matplotlib window."""
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel

        fig = plt.figure(figsize=(self.size / 100, self.size / 100), dpi=100)
        self.animation = self._build(fig)
        plt.show()
        return self

    def __repr__(self) -> str:
        return (
            f"BezierAnimation(degree={len(self.ctrl) - 1}, frames={self.frames}, "
            f"verbose={self.verbose})"
        )
