#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

import numpy as np

from gdpc import Block, geometry, Editor, Box
from glm import ivec3
from gdpc.vector_tools import addY

from buildings import Tower


def buildBounds(
        editor: Editor,
        buildRect: Box,
        y: int
    ) -> None:
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


def buildCastle(
        editor: Editor,
        origin: ivec3,
        palette: list[Block]
    ) -> None:
    """ Place the castle in the build area. """

    height = 30
    
    # place outline walls
    for x1, z1, x2, z2 in [
        (-1, -1, -1, +1),
        (-1, -1, +1, -1),
        (+1, +1, -1, +1),
        (+1, +1, +1, -1)
        ]:
        xz1 = origin + ivec3(x1*11, 0, z1*11)
        xz2 = origin + ivec3(x2*11, height, z2*11)
        geometry.placeCuboid(editor, xz1, xz2, palette)

    # place cylinders (radius 3) at edges of the castle
    for x, z in [(-1, -1), (-1, +1), (+1, +1), (+1, -1)]:
        xz = origin + ivec3(x * 10, 0, z * 10)
        r = 3
        geometry.placeFittingCylinder(
            editor,
            xz + ivec3(-r, 0, -r),
            xz + ivec3(+r, height, +r),
            palette
        )
        geometry.placeFittingCylinder(
            editor,
            xz + ivec3(-2, 0, -2),
            xz + ivec3(+2, height, +2),
            Block('air')
        )

    # hollow out the castle
    geometry.placeCuboid(
        editor,
        origin + ivec3(-10, 0, -10),
        origin + ivec3(+10, height, +10),
        Block('air')
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

def buildBridges(
        editor: Editor,
        towers: list[Tower],
        palette: list[Block]
    ) -> None:
    """ Place the bridges between the towers. """

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
    xrange = range(from_.x+1, to_.x) if from_.x < to_.x else range(from_.x-1, to_.x, -1)
    zrange = range(from_.z+1, to_.z) if from_.z < to_.z else range(from_.z-1, to_.z, -1)
    y = from_.y
    placeRoof: bool = np.random.rand() < .75
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

    supportPalette = [Block(id, {'type': 'top'}) for id in 5 * ['stone_brick_slab'] + 3 * ['mossy_stone_brick_slab']]
    
    for a in arange:
        # calculate where the center of the road is with trigonometry
        if direction == 'x':
            b = round(from_.z + (to_.z - from_.z) * (a - from_.x) / (to_.x - from_.x))
        elif direction == 'z':
            b = round(from_.x + (to_.x - from_.x) * (a - from_.z) / (to_.z - from_.z))
        # build base of the bridge
        for db in [-2, -1, 0, 1, 2]:
            for dy in [-1, 0, 1]:
                if dy == -1:
                    if abs(db) < 2:
                        _placeBlock(a, b + db, y-1, supportPalette)
                        continue
                    else:
                        continue
                if abs(db) < 2 and dy == 1:
                    continue
                _placeBlock(a, b + db, y + dy, palette)
            # check if we should place a roof, otherwise we just skip the rest
            if not placeRoof:
                continue
            # determine what kind of stairs to place for the roof
            stairsDirections = getStairsDirection(direction, arange.step)
            stairsA = 10 * [Block('stone_brick_stairs', {'facing': stairsDirections[0], 'half': 'bottom'})] + \
                5 * [Block('mossy_stone_brick_stairs', {'facing': stairsDirections[0], 'half': 'bottom'})]
            stairsB = 10 * [Block('stone_brick_stairs', {'facing': stairsDirections[1], 'half': 'bottom'})] + \
                5 * [Block('mossy_stone_brick_stairs', {'facing': stairsDirections[1], 'half': 'bottom'})]
            for db in [-2, -1, 0, 1, 2]:
                for dy in [4, 5, 6]:
                    if (abs(db) < 2 and dy == 4):
                        continue
                    if (abs(db) == 2 and dy == 6):
                        continue
                    if (db == -2 and dy == 5):
                        _placeBlock(a, b + db, y + dy, stairsA)
                        continue
                    if (db == 2 and dy == 5):
                        _placeBlock(a, b + db, y + dy, stairsB)
                        continue
                    if (db == 0 and dy == 6):
                        _placeBlock(a, b + db, y + dy, palette)
                        continue
                    if (db == -1 and dy == 6):
                        _placeBlock(a, b + db, y + dy, stairsA)
                        continue
                    if (db == 1 and dy == 6):
                        _placeBlock(a, b + db, y + dy, stairsB)
                        continue
                    _placeBlock(a, b + db, y + dy, palette)
            if not np.random.rand() < .15:
                continue
            # place a pillar on either side of the bridge
            db = np.random.choice([-2, 2])
            for dy in [2, 3]:
                _placeBlock(a, b + db, y + dy, palette)

def getStairsDirection(walkDirection: str, rangeSign: int) -> tuple[str, str]:
    """ Determine the direction of a stairs block for a bridge roof. """
    if walkDirection == 'x' and rangeSign == 1:
            return 'south', 'north'
    elif walkDirection == 'x' and rangeSign == -1:
        return 'south', 'north'
    elif walkDirection == 'z' and rangeSign == 1:
        return 'east', 'west'
    elif walkDirection == 'z' and rangeSign == -1:
        return 'east', 'west'
