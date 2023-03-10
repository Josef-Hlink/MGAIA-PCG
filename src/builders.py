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

    # mm, mp, pp, pm
    directions = [(-1, -1), (-1, +1), (+1, +1), (+1, -1)]
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
        (-35, -35, -20, -20), # mm
        (-35, +20, -20, +35), # mp
        (+20, +20, +35, +35), # pp
        (+20, -35, +35, -20) # pm
    ]
    towers = {district: None for district in ['mm', 'mp', 'pp', 'pm']}
    for (minx, minz, maxx, maxz), district in zip(bounds, towers.keys()):
        x = center.x + np.random.randint(minx, maxx)
        z = center.z + np.random.randint(minz, maxz)

        tower = Tower(
            editor = editor,
            origin = ivec3(x, y, z),
            material = palette,
            heights = [20, 8],
            radii = [10, 11],
            district = district
        )
        tower.build()
        towers[district] = tower
    
    return towers

def buildRoads(
        editor: Editor,
        towers: list[Tower],
        palette: list[Block]
    ) -> None:
    """ Place the roads between the towers. """

    mm, mp, pp, pm = towers.values()
    
    # connect Z entrances
    for from_, to_ in [
        (mm.entrancePZ, mp.entranceMZ),
        (pp.entranceMZ, pm.entrancePZ)
    ]:
        _buildBridge(editor, from_, to_, palette, 'z')

    # connect X entrances
    for from_, to_ in [
        (mp.entrancePX, pp.entranceMX),
        (pm.entranceMX, mm.entrancePX)
    ]:
        _buildBridge(editor, from_, to_, palette, 'x')


def _buildBridge(
        editor: Editor,
        from_: ivec3,
        to_: ivec3,
        palette: list[Block],
        direction: str
    ) -> None:
    """ Place a bridge between two points. """
    xrange = range(from_.x, to_.x) if from_.x < to_.x else range(from_.x, to_.x, -1)
    zrange = range(from_.z, to_.z) if from_.z < to_.z else range(from_.z, to_.z, -1)
    y = from_.y
    placeRoof: bool = np.random.rand() < .99
    arange = xrange if direction == 'x' else zrange

    def _placeBlock(i: int, j: int, y: int, block: Block) -> None:
        if direction == 'x':
            editor.placeBlock(
                ivec3(i, y, j),
                block
            )
        elif direction == 'z':
            editor.placeBlock(
                ivec3(j, y, i),
                block
            )

    for a in arange:
        # calculate where the center of the road is with trigonometry
        if direction == 'x':
            b = round(from_.z + (to_.z - from_.z) * (a - from_.x) / (to_.x - from_.x))
        elif direction == 'z':
            b = round(from_.x + (to_.x - from_.x) * (a - from_.z) / (to_.z - from_.z))
        # build base of the bridge
        for db in [-2, -1, 0, 1, 2]:
            for dy in [0, 1]:
                if abs(db) < 2 and dy == 1:
                    continue
                _placeBlock(a, b + db, y + dy, palette)
            # check if we should place a roof, otherwise we just skip the rest
            if not placeRoof:
                continue
            for db in [-2, -1, 0, 1, 2]:
                for dy in [4, 5]:
                    if (abs(db) < 2 and dy == 4) or (abs(db) == 2 and dy == 5):
                        continue
                    _placeBlock(a, b + db, y + dy, palette)
            if not np.random.rand() < .15:
                continue
            # place a pillar on either side of the bridge
            db = np.random.choice([-2, 2])
            for dy in [2, 3]:
                _placeBlock(a, b + db, y + dy, palette)