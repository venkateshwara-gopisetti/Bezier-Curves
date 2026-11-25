# Contributing to beziervis

Thanks for helping! Bug reports, docs fixes, examples and new features are all welcome. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) in issues and pull requests.

## Ways to help

- **Report a bug** with the [bug report form](https://github.com/venkateshwara-gopisetti/Bezier-Curves/issues/new?template=bug_report.yml). A few lines of code that reproduce it make it much easier to fix.
- **Suggest a feature** with the [feature request form](https://github.com/venkateshwara-gopisetti/Bezier-Curves/issues/new?template=feature_request.yml). For anything big, please open an issue before writing code, so we can agree on the API first.
- **Pick up an issue** labelled [`good first issue`](https://github.com/venkateshwara-gopisetti/Bezier-Curves/labels/good%20first%20issue) or [`help wanted`](https://github.com/venkateshwara-gopisetti/Bezier-Curves/labels/help%20wanted). Leave a comment saying you're working on it.
- **Improve the docs**: typos, clearer explanations and new examples all count.

## Development setup

```bash
git clone https://github.com/venkateshwara-gopisetti/Bezier-Curves
cd Bezier-Curves
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"            # library + numba + matplotlib + pytest + pylint
```

## Checks to run before opening a PR

```bash
pytest                                   # all tests, on every installed backend
BEZIERVIS_BACKEND=numpy pytest           # NumPy only (PowerShell: $env:BEZIERVIS_BACKEND="numpy"; pytest)
pylint src/beziervis benchmarks docs examples   # must stay at 10.00/10
```

CI runs these on Linux, macOS and Windows across Python 3.10–3.13, with and without Numba, and also checks that the core works with NumPy alone.

## Code guidelines

- **Dependencies:** the core (`core.py`, `ops.py`) must import only NumPy. matplotlib belongs in `animation.py` and Numba in `_numba.py`; both are imported lazily.
- **Backend parity:** any new evaluation path must agree with `core.casteljau_numpy` to within `1e-12`. Add it to `test_all_methods_agree`.
- **Inputs:** accept lists or arrays and convert them with `as_control_points()`, which also validates them. Raise `ValueError` with a message that says what was expected.
- **Docstrings:** NumPy style, stating array shapes, e.g. ``(n, d)``.
- **Tests:** every bug fix gets a test that fails without the fix.
- **Performance:** for a change that affects speed, include before and after numbers from `python benchmarks/bench.py` in the PR.
- **Images:** if you change how animations look, regenerate the README images with `python docs/make_assets.py`.

## Pull requests

1. Branch from `master` and keep each PR focused on one change.
2. Fill in the PR template, and update `CHANGELOG.md` under **Unreleased**.
3. Make sure CI passes. A maintainer reviews the PR, usually within a few days.

## Releasing (maintainers)

1. Move the **Unreleased** entries in `CHANGELOG.md` under a new version heading.
2. Bump `__version__` in `src/beziervis/__init__.py`, and `version` and `date-released` in `CITATION.cff`.
3. Merge, then tag the release: `git tag -a vX.Y.Z -m "beziervis X.Y.Z" && git push origin vX.Y.Z`.
4. `publish.yml` checks that the tag matches the version, uploads to PyPI with trusted publishing and creates the GitHub Release.
