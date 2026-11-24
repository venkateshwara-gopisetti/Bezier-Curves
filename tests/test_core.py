import os
import subprocess
import sys

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

import beziervis as bv
from beziervis import core

CUBIC = [[0, 0], [5, 10], [9, 7], [4, 3]]


# --------------------------------------------------------------------------- correctness

def test_docstring_example(backend):
    assert_allclose(bv.points([[0, 0], [1, 2], [2, 0]], n=3), [[0, 0], [1, 1], [2, 0]])


def test_shape_and_endpoints(backend):
    pts = bv.points(CUBIC, n=200)
    assert pts.shape == (200, 2)
    assert_allclose(pts[0], CUBIC[0])
    assert_allclose(pts[-1], CUBIC[-1])


def test_first_point_not_duplicated(backend):
    pts = bv.points(CUBIC, n=50)
    assert len(pts) == 50
    assert not np.allclose(pts[0], pts[1])


def test_quadratic_midpoint(backend):
    p = np.array([[0.0, 0.0], [2.0, 4.0], [4.0, 0.0]])
    mid = bv.points(p, t=[0.5])[0]
    assert_allclose(mid, (p[0] + 2 * p[1] + p[2]) / 4)


def test_linear_is_evenly_spaced(backend):
    pts = bv.points([[0, 0], [10, 0]], n=11)
    assert_allclose(pts[:, 0], np.arange(11), atol=1e-12)


def test_cubic_matches_closed_form(backend):
    p = np.array(CUBIC, dtype=float)
    t = np.linspace(0, 1, 37)[:, None]
    expected = (
        (1 - t) ** 3 * p[0] + 3 * (1 - t) ** 2 * t * p[1] + 3 * (1 - t) * t**2 * p[2] + t**3 * p[3]
    )
    assert_allclose(bv.points(p, t=t.ravel()), expected, atol=1e-12)


@pytest.mark.parametrize("dim", [1, 2, 3, 7])
def test_any_dimension(backend, dim):
    rng = np.random.default_rng(dim)
    ctrl = rng.normal(size=(5, dim))
    pts = bv.points(ctrl, n=20)
    assert pts.shape == (20, dim)
    assert_allclose(pts[[0, -1]], ctrl[[0, -1]], atol=1e-12)


def test_accepts_lists_and_int_arrays(backend):
    a = bv.points(CUBIC, n=10)
    b = bv.points(np.array(CUBIC, dtype=np.int32), n=10)
    assert a.dtype == np.float64
    assert_array_equal(a, b)


def test_degree_zero(backend):
    assert_allclose(bv.points([[3, 4]], n=5), np.tile([3, 4], (5, 1)))


def test_scalar_t(backend):
    assert bv.points(CUBIC, t=0.25).shape == (1, 2)


def test_curve_stays_in_convex_hull_bbox(backend):
    ctrl = bv.random_control_points(8, seed=3)
    pts = bv.points(ctrl, n=500)
    assert np.all(pts >= ctrl.min(axis=0) - 1e-9)
    assert np.all(pts <= ctrl.max(axis=0) + 1e-9)


# --------------------------------------------------------------------------- backend parity

@pytest.mark.parametrize("degree", [1, 2, 3, 5, 10, 20, 30, 31, 45, 60])
def test_all_methods_agree(degree):
    rng = np.random.default_rng(degree)
    ctrl = rng.uniform(-1, 1, size=(degree + 1, 3))
    t = np.linspace(0, 1, 257)
    reference = core.casteljau_numpy(ctrl, t)
    results = {"numpy": core.points_numpy(ctrl, t)}
    if degree <= core.BERNSTEIN_MAX_DEGREE:
        results["bernstein"] = core.bernstein_matrix(degree, t) @ ctrl
    if bv.numba_available():
        from beziervis import _numba

        results["numba_serial"] = _numba.points_serial(ctrl, t)
        results["numba_parallel"] = _numba.points_parallel(ctrl, t)
    for name, result in results.items():
        assert_allclose(result, reference, rtol=0, atol=1e-12, err_msg=name)


def test_high_degree_uses_casteljau():
    ctrl = np.random.default_rng(0).uniform(-1, 1, size=(80, 2))
    t = np.linspace(0, 1, 50)
    assert_array_equal(core.points_numpy(ctrl, t), core.casteljau_numpy(ctrl, t))


def test_parallel_threshold_path(backend):
    # Large enough to take the parallel kernel on the numba backend.
    ctrl = bv.random_control_points(10, seed=1)
    big = bv.points(ctrl, n=50_000)
    assert_allclose(big[::997], bv.points(ctrl, t=np.linspace(0, 1, 50_000)[::997]), atol=1e-12)


# --------------------------------------------------------------------------- batch

def test_points_batch_matches_loop(backend):
    curves = np.random.default_rng(5).normal(size=(12, 4, 3))
    batch = bv.points_batch(curves, n=33)
    assert batch.shape == (12, 33, 3)
    for curve, pts in zip(curves, batch):
        assert_allclose(pts, bv.points(curve, n=33), atol=1e-12)


def test_points_batch_high_degree(backend):
    curves = np.random.default_rng(6).uniform(-1, 1, size=(3, 40, 2))
    batch = bv.points_batch(curves, n=20)
    for curve, pts in zip(curves, batch):
        assert_allclose(pts, core.casteljau_numpy(curve, np.linspace(0, 1, 20)), atol=1e-12)


# --------------------------------------------------------------------------- casteljau_steps

def test_casteljau_steps_structure():
    steps = bv.casteljau_steps(CUBIC, t=0.4)
    assert [s.shape for s in steps] == [(4, 2), (3, 2), (2, 2), (1, 2)]
    assert_allclose(steps[0], CUBIC)
    assert_allclose(steps[-1][0], bv.points(CUBIC, t=0.4)[0], atol=1e-12)


def test_casteljau_steps_first_level_is_lerp():
    p = np.array(CUBIC, dtype=float)
    steps = bv.casteljau_steps(p, t=0.25)
    assert_allclose(steps[1], 0.75 * p[:-1] + 0.25 * p[1:])


# --------------------------------------------------------------------------- validation

@pytest.mark.parametrize(
    "bad",
    [[], [1, 2, 3], [[[1, 2]]], np.empty((0, 2)), np.empty((3, 0)), [[0, np.nan], [1, 1]]],
)
def test_rejects_bad_control_points(bad):
    with pytest.raises(ValueError):
        bv.points(bad)


@pytest.mark.parametrize("n", [0, -3, 2.5])
def test_rejects_bad_n(n):
    with pytest.raises(ValueError):
        bv.points(CUBIC, n=n)


def test_rejects_bad_batch():
    with pytest.raises(ValueError):
        bv.points_batch(CUBIC)


def test_random_control_points_reproducible():
    a = bv.random_control_points(5, seed=42)
    assert_array_equal(a, bv.random_control_points(5, seed=42))
    assert a.shape == (5, 2)
    assert np.all((a >= -100) & (a < 100))


# --------------------------------------------------------------------------- backend selection

def test_set_backend_rejects_unknown():
    with pytest.raises(ValueError):
        bv.set_backend("cuda")


def test_auto_backend():
    previous = bv.get_backend()
    try:
        expected = "numba" if bv.numba_available() else "numpy"
        assert bv.set_backend("auto") == expected
    finally:
        bv.set_backend(previous)


@pytest.mark.parametrize("name", ["numpy", "auto", ""])
def test_env_var_forces_backend(name):
    env = dict(os.environ, BEZIERVIS_BACKEND=name)
    out = subprocess.run(
        [sys.executable, "-c", "import beziervis; print(beziervis.get_backend())"],
        env=env, capture_output=True, text=True, check=True,
    ).stdout.strip()
    expected = name if name not in ("auto", "") else ("numba" if bv.numba_available() else "numpy")
    assert out == expected


def test_core_import_does_not_need_matplotlib_or_numba():
    code = (
        "import sys; import beziervis as bv; bv.set_backend('numpy'); bv.points([[0,0],[1,1]]);"
        "bad = {'matplotlib', 'numba'} & set(sys.modules); assert not bad, bad"
    )
    env = dict(os.environ, BEZIERVIS_BACKEND="numpy")
    subprocess.run([sys.executable, "-c", code], env=env, check=True)
