import numpy as np
import pytest
from numpy.testing import assert_allclose

import beziervis as bv

CUBIC = np.array([[0, 0], [5, 10], [9, 7], [4, 3]], dtype=float)


@pytest.mark.parametrize("t", [0.0, 0.3, 0.5, 0.9, 1.0])
def test_split_reproduces_curve(t):
    left, right = bv.split(CUBIC, t)
    assert left.shape == right.shape == CUBIC.shape
    s = np.linspace(0, 1, 41)
    assert_allclose(bv.points(left, t=s), bv.points(CUBIC, t=s * t), atol=1e-12)
    assert_allclose(bv.points(right, t=s), bv.points(CUBIC, t=t + s * (1 - t)), atol=1e-12)
    assert_allclose(left[-1], right[0])


def test_derivative_matches_finite_difference():
    d = bv.derivative(CUBIC)
    assert d.shape == (3, 2)
    t = np.linspace(0.05, 0.95, 19)
    h = 1e-6
    fd = (bv.points(CUBIC, t=t + h) - bv.points(CUBIC, t=t - h)) / (2 * h)
    assert_allclose(bv.points(d, t=t), fd, atol=1e-6)


def test_derivative_end_tangents():
    d = bv.derivative(CUBIC)
    assert_allclose(d[0], 3 * (CUBIC[1] - CUBIC[0]))
    assert_allclose(d[-1], 3 * (CUBIC[3] - CUBIC[2]))


def test_derivative_degree_zero():
    assert_allclose(bv.derivative([[1, 2, 3]]), [[0, 0, 0]])


@pytest.mark.parametrize("times", [0, 1, 3])
def test_elevate_preserves_shape(times):
    up = bv.elevate(CUBIC, times)
    assert up.shape == (4 + times, 2)
    s = np.linspace(0, 1, 50)
    assert_allclose(bv.points(up, t=s), bv.points(CUBIC, t=s), atol=1e-12)


def test_elevate_rejects_negative():
    with pytest.raises(ValueError):
        bv.elevate(CUBIC, -1)


def test_arc_length_line():
    assert bv.arc_length([[0, 0], [3, 4]]) == pytest.approx(5.0, abs=1e-12)
    # A degree-elevated line has a non-uniform parameterisation but the same length.
    assert bv.arc_length(bv.elevate([[0, 0], [3, 4]], 4)) == pytest.approx(5.0, abs=1e-12)


def test_arc_length_matches_dense_polyline():
    dense = bv.points(CUBIC, n=200_001)
    polyline = np.sum(np.linalg.norm(np.diff(dense, axis=0), axis=1))
    assert bv.arc_length(CUBIC) == pytest.approx(polyline, rel=1e-9)


def test_arc_length_point():
    assert bv.arc_length([[1, 1]]) == 0.0
