import os
import subprocess
import sys

import numpy as np
import pytest

pytest.importorskip("matplotlib")
PIL = pytest.importorskip("PIL.Image")

import beziervis as bv  # noqa: E402
from beziervis.animation import BezierAnimation  # noqa: E402
from beziervis.cli import main, parse_points  # noqa: E402

CUBIC = [[0, 0], [5, 10], [9, 7], [4, 3]]


def _gif_info(path):
    """Return (total duration in ms, size). Pillow merges identical frames, so count time."""
    with PIL.open(path) as img:
        total = 0
        for i in range(img.n_frames):
            img.seek(i)
            total += img.info["duration"]
        return total, img.size


@pytest.mark.parametrize("verbose", [False, True])
def test_save_gif(tmp_path, verbose):
    out = tmp_path / "curve.gif"
    bv.animate(CUBIC, frames=12, hold=3, fps=10, verbose=verbose, size=200).save(str(out))
    duration, size = _gif_info(out)
    assert duration == pytest.approx(1500, abs=20)  # 15 frames at 10 fps
    assert size == (200, 200)


def test_degenerate_curves_render(tmp_path):
    for ctrl in ([[1, 1]], [[0, 0], [1, 1]], [[2, 2], [2, 2], [2, 2]]):
        bv.animate(ctrl, frames=3, hold=0, verbose=True, size=100).save(str(tmp_path / "d.gif"))


def test_many_points_without_labels(tmp_path):
    anim = bv.animate(bv.random_control_points(30, seed=0), frames=3, hold=0, size=100)
    assert anim.labels is False
    anim.save(str(tmp_path / "many.gif"))


def test_trace_follows_curve():
    anim = BezierAnimation(CUBIC, frames=20)
    np.testing.assert_allclose(anim.curve, bv.points(CUBIC, n=20))


def test_jupyter_repr():
    html = bv.animate(CUBIC, frames=4, hold=0, size=100)._repr_html_()
    assert "<script" in html


def test_rejects_non_2d_and_bad_ext(tmp_path):
    with pytest.raises(ValueError):
        bv.animate([[0, 0, 0], [1, 1, 1]])
    with pytest.raises(ValueError):
        bv.animate(CUBIC, frames=3).save(str(tmp_path / "x.png"))


def test_save_does_not_import_pyplot(tmp_path):
    """Saving must work without a display, so it must never touch pyplot."""
    out = tmp_path / "x.gif"
    code = (
        "import sys, beziervis as bv;"
        f"bv.animate({CUBIC}, frames=4, hold=0, size=100).save(r'{out}');"
        "assert 'matplotlib.pyplot' not in sys.modules"
    )
    env = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "MPLBACKEND")}
    subprocess.run([sys.executable, "-c", code], env=env, check=True)
    assert out.exists()


# --------------------------------------------------------------------------- CLI

def test_parse_points():
    np.testing.assert_allclose(parse_points("0,0 5,10 9.5,-7"), [[0, 0], [5, 10], [9.5, -7]])


@pytest.mark.parametrize("bad", ["", "1,2,3", "a,b", "1"])
def test_parse_points_rejects(bad):
    with pytest.raises(Exception):
        parse_points(bad)


def test_cli_save_points(tmp_path, capsys):
    out = tmp_path / "c.gif"
    code = main(["--points", "0,0 5,10 9,7 4,3", "-v", "-f", "5", "--size", "100",
                 "--save", str(out)])
    assert code == 0
    assert out.exists()
    assert "saved" in capsys.readouterr().out


def test_cli_seed_is_reproducible(tmp_path):
    a, b = tmp_path / "a.gif", tmp_path / "b.gif"
    for path in (a, b):
        assert main(["-n", "5", "--seed", "42", "-f", "4", "--size", "100", "-s", str(path)]) == 0
    assert a.read_bytes() == b.read_bytes()


def test_cli_bad_extension(tmp_path):
    assert main(["-n", "3", "-f", "3", "--save", str(tmp_path / "x.txt")]) == 2


def test_cli_module_entry_point(tmp_path):
    out = tmp_path / "m.gif"
    subprocess.run(
        [sys.executable, "-m", "beziervis", "-n", "3", "--seed", "1", "-f", "3",
         "--size", "100", "--save", str(out)],
        check=True, capture_output=True,
    )
    assert out.exists()
