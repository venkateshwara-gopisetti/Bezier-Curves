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

__all__ = [  # pylint: disable=undefined-all-variable  (BezierAnimation is lazy)
    "BERNSTEIN_MAX_DEGREE",
    "BezierAnimation",
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

    See :class:`beziervis.BezierAnimation` for the options.
    """
    from .animation import BezierAnimation  # pylint: disable=import-outside-toplevel

    return BezierAnimation(ctrl, **kwargs)


def __getattr__(name):
    # Lazy so that importing beziervis never imports matplotlib.
    if name == "BezierAnimation":
        from .animation import BezierAnimation  # pylint: disable=import-outside-toplevel

        return BezierAnimation
    raise AttributeError(f"module 'beziervis' has no attribute {name!r}")
