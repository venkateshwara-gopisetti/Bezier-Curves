"""An animated degree-7 curve that ties a loop, with every construction level drawn.

    python examples/loop_animation.py    # writes loop.gif (needs Pillow)

Eight control points around a pentagon-like polygon give a curve that arches over
and loops through itself. With verbose=True, all seven levels of de Casteljau's
construction are drawn in each frame.
"""

from pathlib import Path

import beziervis as bv

LOOP = [[-300, 40], [-40, 150], [300, 60], [120, -150], [-120, -150], [-300, 60], [40, 150],
        [300, 40]]


def main(out_dir=".", frames=90) -> Path:
    """Animate the loop and save it as loop.gif."""
    anim = bv.animate(LOOP, frames=frames, verbose=True, labels=False, size=480, fps=30,
                      hold=30, title="A degree-7 curve ties a loop")
    out = Path(out_dir) / "loop.gif"
    anim.save(str(out))
    return out


if __name__ == "__main__":
    print(main())
