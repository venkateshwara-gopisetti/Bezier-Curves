"""Optional Numba kernels.

Only imported when the "numba" backend is active. Every kernel uses de
Casteljau's algorithm: under JIT the loops are cheap and the method stays
numerically stable at any degree.
"""

import numpy as np
from numba import njit, prange

#: Use the parallel kernel once there are at least this many points to compute.
PARALLEL_THRESHOLD = 20_000


@njit(cache=True, fastmath=False)
def _eval_into(ctrl, t, out, work):
    """Evaluate ``ctrl`` at scalar ``t`` and write the result into ``out``."""
    k, d = ctrl.shape
    for i in range(k):
        for j in range(d):
            work[i, j] = ctrl[i, j]
    s = 1.0 - t
    for level in range(1, k):
        for i in range(k - level):
            for j in range(d):
                work[i, j] = s * work[i, j] + t * work[i + 1, j]
    for j in range(d):
        out[j] = work[0, j]


@njit(cache=True)
def points_serial(ctrl, t):
    """Evaluate one curve at every ``t``, on one thread."""
    out = np.empty((t.shape[0], ctrl.shape[1]))
    work = np.empty_like(ctrl)
    for i in range(t.shape[0]):
        _eval_into(ctrl, t[i], out[i], work)
    return out


@njit(cache=True, parallel=True)
def points_parallel(ctrl, t):
    """Evaluate one curve at every ``t``, split across threads."""
    out = np.empty((t.shape[0], ctrl.shape[1]))
    for i in prange(t.shape[0]):  # pylint: disable=not-an-iterable
        work = np.empty_like(ctrl)
        _eval_into(ctrl, t[i], out[i], work)
    return out


@njit(cache=True, parallel=True)
def batch_parallel(curves, t):
    """Evaluate ``m`` curves at every ``t``, one curve per thread task."""
    m, k, d = curves.shape
    out = np.empty((m, t.shape[0], d))
    for c in prange(m):  # pylint: disable=not-an-iterable
        work = np.empty((k, d))
        for i in range(t.shape[0]):
            _eval_into(curves[c], t[i], out[c, i], work)
    return out


def points(ctrl: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Evaluate one curve, picking the serial or parallel kernel by work size."""
    if t.shape[0] * ctrl.shape[0] >= PARALLEL_THRESHOLD:
        return points_parallel(ctrl, t)
    return points_serial(ctrl, t)


def points_batch(curves: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Evaluate a batch of curves of equal degree; returns (m, n, d)."""
    return batch_parallel(curves, t)
