#!/usr/bin/env python3

"""
Helper functions to make main.py more readable.
"""

import sys

import numpy as np
import matplotlib.pyplot as plt

from gdpc import __url__
from gdpc import Editor, Box, Rect, WorldSlice
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError


def getEditor() -> Editor:
    """ Instantiate an Editor object and check if it can connect to the GDMC HTTP interface. """
    
    editor = Editor()

    try:
        editor.checkConnection()
    except InterfaceConnectionError:
        print(
            f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
            "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
            "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
            f"See {__url__}/README.md for more information."
        )
        sys.exit(1)

    return editor


def getBuildArea(editor: Editor) -> Box:
    """ Get the build area and check if it is set. """
    
    try:
        buildArea = editor.getBuildArea()
    except BuildAreaNotSetError:
        print(
            "Error: failed to get the build area!\n"
            "Make sure to set the build area with the /setbuildarea command in-game.\n"
            "For example: /setbuildarea ~0 ~0 ~0 ~100 ~100 ~100"
        )
        sys.exit(1)

    return buildArea


def createOverview(editor: Editor, buildRect: Rect) -> None:
    """ Create an overview of the worldSlice loaded from the build area. """

    worldSlice: WorldSlice = editor.loadWorldSlice(buildRect)
    heightMap: np.ndarray = worldSlice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    # transpose to get the correct orientation
    heightMap = heightMap.T
    shp = heightMap.shape[0]

    fig, ax = plt.subplots()
    ax.imshow(heightMap, cmap='terrain')
    ax.set_xticks(np.arange(0, shp, 10), np.arange(-shp//2+1, shp//2+1, 10))
    ax.set_yticks(np.arange(0, shp, 10), np.arange(-shp//2+1, shp//2+1, 10))
    ax.set_xlabel('X')
    ax.set_ylabel('Z')

    for label, (x, y) in zip(['NW', 'SW', 'NE', 'SE'], [(5, 5), (5, shp-5), (shp-5, 5), (shp-5, shp-5)]):
        ax.text(x, y, label, color='red', ha='center', va='center')

    fig.tight_layout()
    fig.savefig('../../tmp/overview.png', dpi=300)
    plt.close(fig)
