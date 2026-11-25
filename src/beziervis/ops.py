"""Operations on Bézier curves that return new control points or measurements."""

from __future__ import annotations

from typing import Tuple

import numpy as np

from .core import ArrayLike, as_control_points, casteljau_steps

_GL_NODES, _GL_WEIGHTS = np.polynomial.legendre.leggauss(16)


def split(ctrl: ArrayLike, t: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    """Split a curve at ``t`` into two curves of the same degree.

    Returns ``(left, right)``: ``left`` traces the original over ``[0, t]``
    and ``right`` over ``[t, 1]``, each reparameterised to ``[0, 1]``.
    """
    steps = casteljau_steps(ctrl, t)
    left = np.array([level[0] for level in steps])
    right = np.array([level[-1] for level in reversed(steps)])
    return left, right


def derivative(ctrl: ArrayLike) -> np.ndarray:
    """Return the control points of the derivative (hodograph) curve.

    A degree-``n`` curve has a degree-``n - 1`` derivative with control points
    ``n * (P[i+1] - P[i])``. The derivative of a single point (degree 0) is the
    zero vector, returned as one control point.
    """
    ctrl = as_control_points(ctrl)
    degree = ctrl.shape[0] - 1
    if degree == 0:
        return np.zeros_like(ctrl)
    return degree * np.diff(ctrl, axis=0)


def elevate(ctrl: ArrayLike, times: int = 1) -> np.ndarray:
    """Raise the degree by ``times`` without changing the shape of the curve."""
    ctrl = as_control_points(ctrl)
    if times < 0:
        raise ValueError(f"times must be non-negative; got {times}")
    for _ in range(times):
        n = ctrl.shape[0]  # new degree is n
        alpha = (np.arange(1, n) / n)[:, None]
        middle = alpha * ctrl[:-1] + (1.0 - alpha) * ctrl[1:]
        ctrl = np.vstack([ctrl[:1], middle, ctrl[-1:]])
    return ctrl


def arc_length(ctrl: ArrayLike, segments: int | None = None) -> float:
    """Return the length of the curve.

    Integrates the speed ``|B'(t)|`` with composite 16-point Gauss-Legendre
    quadrature over ``segments`` equal pieces of [0, 1]. The default,
    ``max(8, 4 * degree)``, is accurate to around 1e-10 for typical curves;
    increase it for curves with cusps or very sharp turns.
    """
    from .core import points  # pylint: disable=import-outside-toplevel

    ctrl = as_control_points(ctrl)
    degree = ctrl.shape[0] - 1
    if degree == 0:
        return 0.0
    if segments is None:
        segments = max(8, 4 * degree)
    if segments < 1:
        raise ValueError(f"segments must be at least 1; got {segments}")
    edges = np.linspace(0.0, 1.0, segments + 1)
    half = np.diff(edges)[:, None] / 2.0
    mid = (edges[:-1] + edges[1:])[:, None] / 2.0
    t = (mid + half * _GL_NODES).ravel()
    speed = np.linalg.norm(points(derivative(ctrl), t=t), axis=1)
    return float(np.sum((half * _GL_WEIGHTS).ravel() * speed))
