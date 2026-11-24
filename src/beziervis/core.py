"""NumPy evaluation core and backend selection.

Two evaluation strategies are implemented here:

* **Bernstein matrix** - build the ``(n, k)`` matrix of Bernstein basis values
  once and evaluate every point with a single matrix multiply. This is the
  fastest option for low and moderate degrees.
* **Vectorised de Casteljau** - repeated linear interpolation, applied to all
  parameter values at once. Slower, but numerically stable at any degree, so
  it is used above :data:`BERNSTEIN_MAX_DEGREE`.

If Numba is installed, :func:`points` and :func:`points_batch` dispatch to the
JIT kernels in :mod:`beziervis._numba` instead. Set the environment variable
``BEZIERVIS_BACKEND`` to ``numpy``, ``numba`` or ``auto`` (the default) to
force a choice at import time, or call :func:`set_backend` at runtime.
"""

from __future__ import annotations

import os
from math import comb
from typing import List, Optional, Sequence, Union

import numpy as np

ArrayLike = Union[np.ndarray, Sequence[Sequence[float]]]

#: Highest degree evaluated with the Bernstein matrix; above it, de Casteljau.
BERNSTEIN_MAX_DEGREE = 30

#: Name of the environment variable that forces a backend.
BACKEND_ENV_VAR = "BEZIERVIS_BACKEND"

_BACKENDS = ("auto", "numpy", "numba")
_backend: str = "numpy"


# =============================================================================
# Backend selection
# =============================================================================

def numba_available() -> bool:
    """Return True if Numba can be imported."""
    try:
        import numba  # noqa: F401  pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        return False
    return True


def set_backend(name: str = "auto") -> str:
    """Select the evaluation backend and return the name actually in use.

    Parameters
    ----------
    name : {"auto", "numpy", "numba"}
        ``"auto"`` picks Numba when it is installed and NumPy otherwise.
        ``"numba"`` raises :class:`ImportError` if Numba is not installed.
    """
    global _backend  # pylint: disable=global-statement
    name = name.strip().lower()
    if name not in _BACKENDS:
        raise ValueError(f"unknown backend {name!r}; expected one of {_BACKENDS}")
    if name == "auto":
        name = "numba" if numba_available() else "numpy"
    elif name == "numba" and not numba_available():
        raise ImportError(
            "the 'numba' backend was requested but Numba is not installed; "
            "install it with: pip install beziervis[fast]"
        )
    _backend = name
    return _backend


def get_backend() -> str:
    """Return the name of the backend currently in use ("numpy" or "numba")."""
    return _backend


# =============================================================================
# Input handling
# =============================================================================

def as_control_points(ctrl: ArrayLike) -> np.ndarray:
    """Convert control points to a C-contiguous float64 array of shape (k, d).

    ``k`` is the number of control points (degree + 1) and ``d`` the spatial
    dimension. A one-dimensional curve must be given as shape ``(k, 1)``.
    """
    arr = np.ascontiguousarray(ctrl, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(
            f"control points must have shape (k, d); got an array with shape {arr.shape}"
        )
    if arr.shape[0] < 1 or arr.shape[1] < 1:
        raise ValueError(f"need at least one control point of dimension >= 1; got {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("control points must be finite")
    return arr


def _as_batch(curves: ArrayLike) -> np.ndarray:
    arr = np.ascontiguousarray(curves, dtype=np.float64)
    if arr.ndim != 3 or 0 in arr.shape:
        raise ValueError(
            "curves must have shape (m, k, d): m curves of k control points each; "
            f"got {arr.shape}"
        )
    if not np.all(np.isfinite(arr)):
        raise ValueError("control points must be finite")
    return arr


def parameter_values(n: int = 100, t: Optional[ArrayLike] = None) -> np.ndarray:
    """Return parameter values: ``t`` if given, else ``n`` evenly spaced in [0, 1]."""
    if t is not None:
        arr = np.ascontiguousarray(t, dtype=np.float64)
        if arr.ndim == 0:
            arr = arr.reshape(1)
        if arr.ndim != 1:
            raise ValueError(f"t must be a scalar or 1-D array; got shape {arr.shape}")
        return arr
    if int(n) != n or n < 1:
        raise ValueError(f"n must be a positive integer; got {n!r}")
    return np.linspace(0.0, 1.0, int(n))


# =============================================================================
# NumPy kernels
# =============================================================================

def bernstein_matrix(degree: int, t: np.ndarray) -> np.ndarray:
    """Return the ``(len(t), degree + 1)`` matrix of Bernstein basis values."""
    i = np.arange(degree + 1)
    coeffs = np.array([comb(degree, j) for j in i], dtype=np.float64)
    t = np.asarray(t, dtype=np.float64)[:, None]
    return coeffs * t**i * (1.0 - t) ** (degree - i)


def casteljau_numpy(ctrl: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Evaluate with de Casteljau's algorithm, vectorised over ``t``."""
    work = np.broadcast_to(ctrl, (t.shape[0],) + ctrl.shape)
    tt = t[:, None, None]
    st = 1.0 - tt
    for _ in range(ctrl.shape[0] - 1):
        work = st * work[:, :-1] + tt * work[:, 1:]
    return np.ascontiguousarray(work[:, 0])


def points_numpy(ctrl: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Evaluate one curve with NumPy, choosing the method by degree."""
    degree = ctrl.shape[0] - 1
    if degree <= BERNSTEIN_MAX_DEGREE:
        return bernstein_matrix(degree, t) @ ctrl
    return casteljau_numpy(ctrl, t)


def points_batch_numpy(curves: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Evaluate ``m`` curves of equal degree with NumPy; returns (m, n, d)."""
    degree = curves.shape[1] - 1
    if degree <= BERNSTEIN_MAX_DEGREE:
        return np.einsum("nk,mkd->mnd", bernstein_matrix(degree, t), curves)
    return np.stack([casteljau_numpy(c, t) for c in curves])


# =============================================================================
# Public API
# =============================================================================

def points(ctrl: ArrayLike, n: int = 100, t: Optional[ArrayLike] = None) -> np.ndarray:
    """Evaluate a Bézier curve.

    Parameters
    ----------
    ctrl : array_like, shape (k, d)
        Control points; a list of lists works. Any dimension ``d``.
    n : int, default 100
        Number of evenly spaced samples in [0, 1], including both end points.
        Ignored when ``t`` is given.
    t : array_like, optional
        Explicit parameter values to evaluate at.

    Returns
    -------
    numpy.ndarray, shape (n, d)
        Points on the curve. The first row is ``ctrl[0]`` and the last is
        ``ctrl[-1]``.

    Examples
    --------
    >>> import beziervis as bv
    >>> bv.points([[0, 0], [1, 2], [2, 0]], n=3)
    array([[0., 0.],
           [1., 1.],
           [2., 0.]])
    """
    ctrl = as_control_points(ctrl)
    tv = parameter_values(n, t)
    if _backend == "numba":
        from . import _numba  # pylint: disable=import-outside-toplevel
        return _numba.points(ctrl, tv)
    return points_numpy(ctrl, tv)


def points_batch(curves: ArrayLike, n: int = 100, t: Optional[ArrayLike] = None) -> np.ndarray:
    """Evaluate many curves of the same degree at once.

    Parameters
    ----------
    curves : array_like, shape (m, k, d)
        ``m`` curves with ``k`` control points each.
    n, t
        As in :func:`points`.

    Returns
    -------
    numpy.ndarray, shape (m, n, d)
    """
    arr = _as_batch(curves)
    tv = parameter_values(n, t)
    if _backend == "numba":
        from . import _numba  # pylint: disable=import-outside-toplevel
        return _numba.points_batch(arr, tv)
    return points_batch_numpy(arr, tv)


def casteljau_steps(ctrl: ArrayLike, t: float) -> List[np.ndarray]:
    """Return every level of de Casteljau's construction at parameter ``t``.

    Level 0 is the control polygon, of shape ``(k, d)``. Each later level
    interpolates between neighbouring points of the previous one, so level
    ``j`` has shape ``(k - j, d)``. The final level holds a single point: the
    curve evaluated at ``t``.
    """
    level = as_control_points(ctrl)
    t = float(t)
    steps = [level]
    while level.shape[0] > 1:
        level = (1.0 - t) * level[:-1] + t * level[1:]
        steps.append(level)
    return steps


def random_control_points(
    n: int,
    seed: Optional[int] = None,
    low: float = -100.0,
    high: float = 100.0,
    dim: int = 2,
) -> np.ndarray:
    """Return ``n`` random integer-valued control points in ``[low, high)``."""
    if n < 1:
        raise ValueError(f"n must be at least 1; got {n}")
    rng = np.random.default_rng(seed)
    return rng.integers(int(low), int(high), size=(n, dim)).astype(np.float64)


set_backend(os.environ.get(BACKEND_ENV_VAR) or "auto")
