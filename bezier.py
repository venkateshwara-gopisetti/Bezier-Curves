# -*- coding: utf-8 -*-
"""
Created on Sat May 14 00:19:35 2022

@author: Venkat
"""

# =============================================================================
# Importing Libraries
# =============================================================================

import argparse
import matplotlib.pyplot as plt

from src.bezier_curve import generate_start_points, generate_bezier_curve

def main():
    parser = argparse.ArgumentParser(
        prog="Bezier Curve",
        description="A cli utility to generate bezier curve with some inputs.",
        epilog="And that's how you generate the Bezier Curve."
    )
    parser.add_argument("-n", help="Number of seed points", type=int, required=True)
    parser.add_argument("-f", "--frames", help="Number of frames to generate", type=int, default=100)
    parser.add_argument("-v", "--verbose", help="Display intermediate bezier curves",
                        action="store_true")
    args = parser.parse_args()

    points = generate_start_points(args.n)

    generate_bezier_curve(points, frame_count=args.frames, verbose=args.verbose)
    plt.show()

if __name__=="__main__":
    main()