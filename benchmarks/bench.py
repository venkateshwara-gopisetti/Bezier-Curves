"""Benchmark the evaluation methods.

    python benchmarks/bench.py            # prints a Markdown table

Times are the best of several repeats, after a warm-up call so that Numba's
JIT compilation is not counted.
"""

# pylint: disable=cell-var-from-loop  # lambdas are called within the same iteration
import timeit

import numpy as np

import beziervis as bv
from beziervis import core

CASES = [  # (label, degree, samples, curves)
    ("cubic, 1k points", 3, 1_000, 1),
    ("cubic, 1M points", 3, 1_000_000, 1),
    ("degree 10, 100k points", 10, 100_000, 1),
    ("degree 50, 100k points", 50, 100_000, 1),
    ("10k cubics x 100 points", 3, 100, 10_000),
]


def naive(ctrl, t):
    """Pure-Python de Casteljau, one point at a time (the original approach)."""
    out = []
    for ti in t:
        level = [tuple(p) for p in ctrl]
        while len(level) > 1:
            level = [
                tuple((1 - ti) * a + ti * b for a, b in zip(p, q))
                for p, q in zip(level, level[1:])
            ]
        out.append(level[0])
    return np.array(out)


def best(fn, repeat=5):
    """Return the best time per call, in seconds."""
    fn()  # warm-up (JIT compile, caches)
    number = 1
    while timeit.timeit(fn, number=number) < 0.2 and number < 1_000:
        number *= 2
    return min(timeit.repeat(fn, number=number, repeat=repeat)) / number


def fmt(seconds):
    """Format a duration with a readable unit."""
    if seconds is None:
        return "-"
    for unit, scale in (("s", 1), ("ms", 1e-3), ("us", 1e-6)):
        if seconds >= scale:
            return f"{seconds / scale:.3g} {unit}"
    return f"{seconds / 1e-9:.3g} ns"


def main():
    """Run every case and print a Markdown table."""
    rng = np.random.default_rng(0)
    methods = ["naive Python", "NumPy Bernstein", "NumPy de Casteljau"]
    if bv.numba_available():
        from beziervis import _numba  # pylint: disable=import-outside-toplevel

        methods += ["Numba serial", "Numba parallel"]
    print("| case | " + " | ".join(methods) + " |")
    print("|---" * (len(methods) + 1) + "|")
    for label, degree, n, m in CASES:
        t = np.linspace(0, 1, n)
        row = []
        if m == 1:
            ctrl = rng.uniform(-1, 1, size=(degree + 1, 2))
            fns = {
                "naive Python": (lambda: naive(ctrl, t[: min(n, 10_000)])) if n <= 10_000 else None,
                "NumPy Bernstein": (lambda: core.bernstein_matrix(degree, t) @ ctrl)
                if degree <= core.BERNSTEIN_MAX_DEGREE else None,
                "NumPy de Casteljau": lambda: core.casteljau_numpy(ctrl, t),
            }
            if bv.numba_available():
                fns["Numba serial"] = lambda: _numba.points_serial(ctrl, t)
                fns["Numba parallel"] = lambda: _numba.points_parallel(ctrl, t)
        else:
            curves = rng.uniform(-1, 1, size=(m, degree + 1, 2))
            fns = {
                "naive Python": None,
                "NumPy Bernstein": lambda: core.points_batch_numpy(curves, t),
                "NumPy de Casteljau": None,
            }
            if bv.numba_available():
                fns["Numba serial"] = None
                fns["Numba parallel"] = lambda: _numba.batch_parallel(curves, t)
        for name in methods:
            fn = fns.get(name)
            row.append(fmt(best(fn)) if fn else "-")
        print(f"| {label} | " + " | ".join(row) + " |")


if __name__ == "__main__":
    main()
