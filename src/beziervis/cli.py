"""Command-line interface: ``beziervis`` (or ``python -m beziervis``).

Examples::

    beziervis --points "0,0 5,10 9,7 4,3" --verbose --save curve.gif
    beziervis -n 5 --seed 42
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

import numpy as np

from . import __version__
from .core import random_control_points


def parse_points(text: str) -> np.ndarray:
    """Parse ``"x0,y0 x1,y1 ..."`` into a (k, 2) array."""
    try:
        pts = [[float(v) for v in pair.split(",")] for pair in text.split()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"could not parse points {text!r}: {exc}") from exc
    if not pts:
        raise argparse.ArgumentTypeError("no points given")
    if any(len(p) != 2 for p in pts):
        raise argparse.ArgumentTypeError(
            f"each point must be 'x,y' with points separated by spaces; got {text!r}"
        )
    return np.array(pts)


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="beziervis",
        description="Animate a Bézier curve being built by de Casteljau's algorithm.",
        epilog='Example: beziervis --points "0,0 5,10 9,7 4,3" --verbose --save curve.gif',
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--points", "-p", type=parse_points, metavar='"x,y x,y ..."',
                     help="control points, space-separated")
    src.add_argument("-n", type=int, default=4, metavar="N",
                     help="number of random control points (default: 4)")
    parser.add_argument("--seed", type=int, help="random seed, for reproducible points")
    parser.add_argument("-f", "--frames", type=int, default=100,
                        help="number of animation steps (default: 100)")
    parser.add_argument("--fps", type=int, default=30, help="frames per second (default: 30)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="draw the intermediate construction lines")
    parser.add_argument("--no-labels", action="store_true", help="hide point labels")
    parser.add_argument("--size", type=int, default=600,
                        help="figure size in pixels (default: 600)")
    parser.add_argument("-s", "--save", metavar="FILE",
                        help="save to .gif or .mp4 instead of opening a window")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.points is None and args.n < 1:
        parser.error("-n must be at least 1")

    try:
        from .animation import BezierAnimation  # pylint: disable=import-outside-toplevel
    except ImportError as exc:
        print(f"beziervis: {exc}", file=sys.stderr)
        return 1

    ctrl = args.points if args.points is not None else random_control_points(args.n, args.seed)
    try:
        anim = BezierAnimation(
            ctrl, frames=args.frames, verbose=args.verbose,
            labels=False if args.no_labels else None, fps=args.fps, size=args.size,
        )
        if args.save:
            anim.save(args.save)
            print(f"saved {args.save}")
        else:
            anim.show()
    except (ValueError, RuntimeError) as exc:
        print(f"beziervis: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
