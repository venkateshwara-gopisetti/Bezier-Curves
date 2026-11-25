"""Every script in examples/ runs and writes its image."""

import runpy
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
pytest.importorskip("PIL")

EXAMPLES = sorted((Path(__file__).parent.parent / "examples").glob("*.py"))


def test_examples_found():
    assert len(EXAMPLES) >= 10


@pytest.mark.parametrize("script", EXAMPLES, ids=lambda p: p.stem)
def test_example_runs(script, tmp_path):
    main = runpy.run_path(str(script))["main"]
    out = main(tmp_path, frames=10) if script.stem == "loop_animation" else main(tmp_path)
    assert Path(out).parent == tmp_path
    assert Path(out).stat().st_size > 1000
