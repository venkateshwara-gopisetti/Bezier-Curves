# Changelog

All notable changes are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-11-25

The repository is relaunched as the `beziervis` package.

### Added
- `points()`: Bernstein-matrix evaluation, switching to vectorised de Casteljau above degree 30. Works in any dimension and accepts lists or arrays.
- `points_batch()`, `casteljau_steps()`, `split()`, `derivative()`, `elevate()`, `arc_length()`.
- Optional Numba backend, with serial and parallel kernels, chosen automatically. Override it with `BEZIERVIS_BACKEND` or `set_backend()`.
- `animate()` / `BezierAnimation`, built on matplotlib's `FuncAnimation`: `.show()`, `.save()` to GIF or MP4, and inline display in Jupyter. Saving works without a display.
- `beziervis` command (also `python -m beziervis`), with `--points`, `--seed`, `--frames`, `--fps`, `--save` and more.
- Test suite (backend parity, edge cases, CLI), benchmarks, quickstart notebook, and CI on Linux, macOS and Windows for Python 3.10–3.13.

### Changed
- **The license changed from GPL-3.0 to MIT.**
- matplotlib is now optional (`pip install beziervis[anim]`).
- Animation axes fit the control points instead of a fixed ±100 window.

### Fixed
- The first point of the curve is no longer duplicated.

### Removed
- The `bezier.py` script and `src/bezier_curve.py`, replaced by the `beziervis` command and package.

[Unreleased]: https://github.com/venkateshwara-gopisetti/Bezier-Curves/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/venkateshwara-gopisetti/Bezier-Curves/releases/tag/v1.0.0
