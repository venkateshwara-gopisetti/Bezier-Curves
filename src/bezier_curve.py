# -*- coding: utf-8 -*-
"""
Created on Wed May 11 02:27:55 2022

@author: Venkat
"""

# =============================================================================
# Importing Libraries
# =============================================================================

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import rgb2hex

# =============================================================================
# Custom Functions
# =============================================================================

def lin_bez(frame: float, points_list: list) -> np.array:
    """
    Linear Bezier Curve function.
    Parameters
    ----------
    frame : float
        index at which to calculate bezier on.
    points_list : list
        list of points to calculate bezier curve on.
    Returns
    -------
    np.array
        coordinates of the bezier point.
    """
    point0, point1 = points_list
    return np.sum([np.multiply(1-frame, point0), np.multiply(frame, point1)], axis=0).reshape(1,2)

def plot_line(color_list: list, label: str, points_list: list) -> list:
    """
    Plots lines between an ordered list of points.
    Parameters
    ----------
    color_list : list
        list of colors for each line.
    label : str
        prefix for the group of lines.
    points_list : list
        list of points to draw lines on.
    Returns
    -------
    list
        list of plot objects (lines and text).
    """
    lines = list(points_list)
    plots = []
    # For each consecutive pair of points, plot a line and the text label on starting point.
    for ind in range(len(lines)-1):
        xseries,yseries = np.array(lines[ind:ind+2]).T
        plots.append(plt.plot(xseries, yseries, color_list[ind], alpha=0.5))
        plots.append(plt.annotate(f'{label}{ind}', lines[ind]))
    # plot the label on last point.
    plots.append(plt.annotate('{label}{ind+1}', lines[ind+1]))
    # return plot objects for garbage collection.
    return plots

def gc_plot_objects(objs):
    """collection of matplotlib objects to remove from the plot figure.
    """
    for line_obj in objs:
        if isinstance(line_obj, list):
            line_obj[0].remove()
        else:
            line_obj.set_visible(False)

# pylint: disable=R0914
def generate_bezier_curve(points: list, frame_count:int = 100, verbose: bool=False):
    """
    Function that takes in a list of seed points and generates a bezier curve.
    Parameters
    ----------
    points : list
        list of seed points.
    frame_count : int
        number of frames to generate the curve on. The default is 100.
    verbose : bool, optional
        Verbosity for the graphing.
        If False, only original points, lines and final bezier curve is plotted.
        If True, all the intermediary bezier curves are plotted.
        The default is False. For aesthetics, set to False when N>5.
    Returns
    -------
    None.
    """
    tframe = np.linspace(0, 1, frame_count)

    curve_levels = len(points)

    fig = plt.figure(figsize=(12,8))
    fig.suptitle(f'Bezier Curve (order-{curve_levels})', fontsize=20)
    plt.axis([-100, 100, -100, 100])

    level_labels = [chr(ord('A')+k) for k in range (curve_levels)]

    # Array to store bezier curve coordinates.
    bt_curve = np.array(points[0].reshape(1,2))

    # Data Structure to store coordinates for each frame.
    # Frame - Visual Frame
    # -Level - (Each bezier curve of order N, has N groups of lines.
    #           First set of lines from the seed points, and then each
    #           consecutive line group for intermediate bezier curves.
    # --Part - Each line in a level is called a part.
    graph_stack = {
        frame:{
            level:{
                part:None for part in range(curve_levels-level)
            } for level in range(curve_levels)
        } for frame in range(len(tframe))
    }
    # Structure to store plot objects from last frame for garbage collection.
    plot_stack = {level:None for level in range(curve_levels)}

    # Dividing Viridis color map into equivalent colors as many lines are there.
    cmap = plt.cm.viridis(np.linspace(0,1,int(np.ceil(curve_levels*(curve_levels-1)/2))))

    # Conversion from array to hex
    cmap = [rgb2hex(ele[:3]) for ele in cmap]

    # Assignment of color to line.
    color_list = []
    cnt = 0
    for level in range(1, curve_levels):
        color_list.append(cmap[cnt:cnt+(curve_levels-level)])
        cnt+=level

    # Plot seed points and lines.
    plot_line(color_list[0], level_labels[0], points)

    # Generate curve for each frame.
    for frame_index, frame_time in enumerate(tframe):
        for ind, pnt in enumerate(points):
            graph_stack[frame_index][0][ind] = pnt.reshape(1,2)
        for level in range(1, curve_levels):
            for part in graph_stack[frame_index][level].keys():
                points_to_use = [
                    graph_stack[frame_index][level-1][part],
                    graph_stack[frame_index][level-1][part+1]
                ]
                graph_stack[frame_index][level][part] = \
                    lin_bez(
                        frame_time,
                        points_to_use
                    )
            # if last level, draw bezier point for current frame.
            if level == curve_levels-1:
                bt_curve = np.append(bt_curve, graph_stack[frame_index][level][0], axis=0)
                xseries, yseries = bt_curve.T
                bezier_plot_object = \
                    plt.plot(
                        xseries,
                        yseries,
                        label="Bezier Curve",
                        color='black',
                        linewidth=0.5
                    )
            else:
                # If verbose, draw intermediate bezier curves.
                if verbose:
                    if plot_stack[level] is not None:
                        gc_plot_objects(plot_stack[level])
                    plot_stack[level] = \
                        plot_line(
                            color_list[level-1],
                            level_labels[level],
                            [x[-1] for x in graph_stack[frame_index][level].values()]
                        )
                else:
                    continue
        plt.pause(0.01)
    # if verbose remove final labels.
    if verbose:
        for level in range(1, curve_levels-1):
            gc_plot_objects(plot_stack[level])
    plt.legend(handles=[bezier_plot_object[0]])
    plt.pause(0.01)


def generate_start_points(n_points: int=3) -> list:
    """
    Generate N starting points for the curve.
    Parameters
    ----------
    n_points : int
        Number of points to generate.
    Returns
    -------
    list
        listr of starting points.
    """
    points = np.random.randint(-100, 100, (n_points, 2))
    return points

if __name__ == "__main__":
    seed_points = generate_start_points(n_points=5)
    generate_bezier_curve(points=seed_points, verbose=True)
    plt.show()
