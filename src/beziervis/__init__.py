"""beziervis - evaluate, manipulate and animate Bézier curves.

>>> import beziervis as bv
>>> pts = bv.points([[0, 0], [5, 10], [9, 7], [4, 3]], n=200)
>>> pts.shape
(200, 2)

The core needs only NumPy. ``pip install beziervis[fast]`` adds Numba
kernels, which are used automatically; ``pip install beziervis[anim]`` adds
matplotlib for :func:`animate`.
"""

from .core import (
    BERNSTEIN_MAX_DEGREE,
    bernstein_matrix,
    casteljau_steps,
    get_backend,
    numba_available,
    points,
    points_batch,
    random_control_points,
    set_backend,
)
from .ops import arc_length, derivative, elevate, split

__version__ = "1.0.0"

__all__ = [
    "BERNSTEIN_MAX_DEGREE",
    "animate",
    "arc_length",
    "bernstein_matrix",
    "casteljau_steps",
    "derivative",
    "elevate",
    "get_backend",
    "numba_available",
    "points",
    "points_batch",
    "random_control_points",
    "set_backend",
    "split",
]


def animate(ctrl, **kwargs):
    """Build an animation of de Casteljau's construction (needs matplotlib).

    See :class:`beziervis.animate.BezierAnimation` for the options.
    """
    from .animate import BezierAnimation  # pylint: disable=import-outside-toplevel

    return BezierAnimation(ctrl, **kwargs)
