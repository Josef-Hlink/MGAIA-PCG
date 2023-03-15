#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

import numpy as np

from gdpc import geometry, Editor, Box
from glm import ivec3
from gdpc.vector_tools import addY, Y, X

from structs.tower import TowerBase, TowerRoom, TowerRoof, Tower, TowerRoofAccess, TowerStairway
from structs.bridge import Bridge
from structs.castle import CastleOutline, CastleBasement, CastleRoof, CastleTree, CastleEntrance, Castle
from generators import line3D
from materials import BasePalette, BaseStairPalette, Concrete, CryingObsidian, TintedGlass


def buildBounds(editor: Editor, buildRect: Box, y: int) -> None:
    """ Place the bounds of the build area. """

    center: ivec3 = addY(buildRect.center, y)
    geometry.placeRectOutline(editor, buildRect, center.y, Concrete('white'))

    # NW, SW, SE, NE
    # negative x is east
    # positive x is west
    # negative z is north
    # positive z is south
    directions = [(-1, -1), (-1, +1), (+1, +1), (+1, -1)]
    colors = ['blue', 'yellow', 'green', 'red']

    for (x, z), color in zip(directions, colors):
        xz = center + ivec3(x * 50, 0, z * 50)
        editor.placeBlock(line3D(xz, xz + ivec3(0, 10, 0)), Concrete(color))


def buildTowers(editor: Editor, center: ivec3, dry: bool = False) -> dict[str, Tower]:
    """
    Place the towers of the build area.
    Returns a dictionary with the towers.
    """

    basePalette = BasePalette()
    baseStairPalette = BaseStairPalette()

    # create four 2D sectors (10x10) where the center of a tower will be chosen
    bounds = [
        (-35, -35, -25, -25), # NW
        (-35, +25, -25, +35), # SW
        (+25, +25, +35, +35), # SE
        (+25, -35, +35, -25)  # NE
    ]
    towers = {district: None for district in ['nw', 'sw', 'se', 'ne']}
    for (minx, minz, maxx, maxz), district in zip(bounds, towers.keys()):
        x = center.x + np.random.randint(minx, maxx)
        z = center.z + np.random.randint(minz, maxz)

        towerBase = TowerBase(
            origin = ivec3(x, center.y, z),
            district = district,
            material = basePalette,
            height = 20,
            radius = 10
        )
        towerRoom = TowerRoom(
            origin = towerBase.o + Y * towerBase.height,
            material = basePalette,
            height = 8,
            radius = 11
        )
        towerRoof = TowerRoof(
            origin = towerRoom.o + Y * towerRoom.height,
            baseMaterial = basePalette,
            coneMaterial = CryingObsidian,
            beaconColor = 'purple',
            height = 10,
            radius = 13
        )
        sign = -1 if district in ['nw', 'sw'] else 1
        towerRoofAccess = TowerRoofAccess(
            origin = towerRoof.o + sign * X * (towerRoom.radius-1),
            district = district, 
            baseMaterial = basePalette,
            stairMaterial = baseStairPalette,
            gateMaterial = CryingObsidian,
            roomHeight = towerRoom.height
        )
        tower = Tower(
            district = district,
            base = towerBase,
            room = towerRoom,
            roof = towerRoof,
            roofAccess = towerRoofAccess
        )

        if not dry:
            tower.place(editor)
        towers[district] = tower

    return towers


def buildCastle(editor: Editor, center: ivec3) -> Castle:
    """
    Place the castle in the center of the towers.
    Returns the castle.
    """

    basePalette = BasePalette()

    castleOutline = CastleOutline(
        origin = center,
        baseMaterial = basePalette,
        wallHeight = 30,
        basementHeight = 10,
        width = 10
    )
    castleBasement = CastleBasement(
        origin = castleOutline.o - Y * castleOutline.basementHeight,
        baseMaterial = basePalette,
        beaconColor = 'black',
        width = castleOutline.width,
    )
    castleRoof = CastleRoof(
        origin = center + Y * (castleOutline.wallHeight+1),
        corners = castleOutline.corners,
        roofMaterial = TintedGlass,
        height = 8
    )
    castleTree = CastleTree(
        origin = center + Y,
        maxTrunkHeight = 20
    )
    castle = Castle(
        outline = castleOutline,
        basement = castleBasement,
        roof = castleRoof,
        tree = castleTree
    )

    castle.place(editor)

    return castle


def buildBridges(editor: Editor, towers: dict[str, Tower]) -> list[Bridge]:
    """
    Place the bridges between the towers.
    Returns a list of the bridges.
    """

    bridges = []
    
    basePalette = BasePalette()
    baseStairPalette = BaseStairPalette()
    noRoof = np.random.randint(0, 4)

    nw, sw, se, ne = towers.values()
    for i, towerSet in enumerate([(nw, sw), (nw, ne), (sw, se), (ne, se)]):
        bridge = Bridge(
            towers = towerSet,
            baseMaterial = basePalette,
            stairMaterial = baseStairPalette,
            hasRoof = False if i == noRoof else True
        )
        bridge.place(editor)
        bridges.append(bridge)
    
    return bridges


def buildEntryPoints(editor: Editor, castle: Castle, towers: dict[str, Tower]) -> TowerStairway:
    """
    Place a stairway around one randomly chosen tower.
    On the opposite district, the castle entrance will be placed.
    Returns the stairway and the castle entrance.
    """

    dT = np.random.choice(['nw', 'sw', 'se', 'ne'])
    tower = towers[dT]
    towerStairway = TowerStairway(
        towerBase = tower.base,
        material = BaseStairPalette()
    )
    towerStairway.place(editor)

    dC = {'nw': 'se', 'sw': 'ne', 'se': 'nw', 'ne': 'sw'}[dT]

    castleEntrance = CastleEntrance(
        origin = castle.outline.corners[dC] + 20 * Y,
        district = dC,
        material = BasePalette()
    )
    castleEntrance.place(editor)

    return towerStairway, castleEntrance
