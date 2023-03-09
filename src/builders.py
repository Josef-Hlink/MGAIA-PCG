#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

import numpy as np

from gdpc import Block, geometry, Editor, Box
from glm import ivec3
from gdpc.vector_tools import addY

from buildings import Tower


def buildBounds(editor: Editor, buildRect: Box, y: int) -> None:
    """ Place the bounds of the build area. """

    center: ivec3 = addY(buildRect.center, y)

    geometry.placeRectOutline(editor, buildRect, center.y, Block("red_concrete"))

    directions = [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]
    colors = ['blue', 'yellow', 'green', 'red']
    for (x, z), color in zip(directions, colors):
        xz = center + ivec3(x * 50, 0, z * 50)
        geometry.placeLine(
            editor,
            xz,
            xz + ivec3(0, 10, 0),
            Block(f'{color}_concrete')
        )

def buildTowers(
        editor: Editor,
        buildRect: Box,
        y: int,
        palette: list[Block]
    ) -> dict[str, Tower]:
    """ Place the towers of the build area and return them. """

    center: ivec3 = addY(buildRect.center, y)

    # create four 2D sectors (15x15) where the center of a tower will be chosen
    bounds = [
        (-35, -35, -20, -20), # SW
        (-35, +20, -20, +35), # SE
        (+20, +20, +35, +35), # NE
        (+20, -35, +35, -20) # NW
    ]
    towers = {district: None for district in ['SW', 'SE', 'NE', 'NW']}
    for (minx, miny, maxx, maxy), district in zip(bounds, towers.keys()):
        x = center.x + np.random.randint(minx, maxx)
        z = center.z + np.random.randint(miny, maxy)

        tower = Tower(
            origin = ivec3(x, y, z),
            material = palette,
            heights = [10, 8],
            radii = [10, 11],
            district = district
        )
        tower.build(editor)
        towers[district] = tower
    
    return towers

def buildRoads(
        editor: Editor,
        towers: list[Tower],
        palette: list[Block]
    ) -> None:
    """ Place the roads between the towers. """

    for from_, to_ in [('SW', 'SE'), ('SE', 'NE'), ('NE', 'NW'), ('NW', 'SW')]:
        # base of road
        tower1 = towers[from_]
        tower2 = towers[to_]
        geometry.placeLine(
            editor,
            tower1.origin + ivec3(0, 11, 0),
            tower2.origin + ivec3(0, 11, 0),
            palette,
            width = 3
        )
        # excavate area above (openings in the towers)
        for y in range(12, 15):
            geometry.placeLine(
                editor,
                tower1.origin + ivec3(0, y, 0),
                tower2.origin + ivec3(0, y, 0),
                Block('air'),
                width = 3
            )
        # road surface
        geometry.placeLine(
            editor,
            tower1.origin + ivec3(0, 10, 0),
            tower2.origin + ivec3(0, 10, 0),
            palette
        )
    