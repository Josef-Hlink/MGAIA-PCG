#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

import numpy as np

from gdpc import geometry, Editor, Box
from glm import ivec3
from gdpc.vector_tools import addY, Y, X

from tower import TowerBase, TowerRoom, TowerRoof, Tower, TowerRoofAccess
from bridge import Bridge
from bigtree import BigTree
from castle import CastleOutline, CastleRoof, Castle
from generators import line3D
from materials import BasePalette, BaseStairPalette, CryingObsidian, TintedGlass, Concrete


def buildBounds(editor: Editor, buildRect: Box, y: int) -> None:
    """ Place the bounds of the build area. """

    center: ivec3 = addY(buildRect.center, y)
    geometry.placeRectOutline(editor, buildRect, center.y, Concrete('white'))

    # mm, mp, pp, pm
    directions = [(-1, -1), (-1, +1), (+1, +1), (+1, -1)]
    colors = ['blue', 'yellow', 'green', 'red']

    for (x, z), color in zip(directions, colors):
        xz = center + ivec3(x * 50, 0, z * 50)
        editor.placeBlock(line3D(xz, xz + ivec3(0, 10, 0)), Concrete(color))


def buildTowers(editor: Editor, center: ivec3) -> dict[str, Tower]:
    """
    Place the towers of the build area.
    Returns a dictionary with the towers.
    """

    basePalette = BasePalette()
    baseStairPalette = BaseStairPalette()

    # create four 2D sectors (10x10) where the center of a tower will be chosen
    bounds = [
        (-35, -35, -25, -25), # mm
        (-35, +25, -25, +35), # mp
        (+25, +25, +35, +35), # pp
        (+25, -35, +35, -25)  # pm
    ]
    towers = {district: None for district in ['mm', 'mp', 'pp', 'pm']}
    for (minx, minz, maxx, maxz), district in zip(bounds, towers.keys()):
        x = center.x + np.random.randint(minx, maxx)
        z = center.z + np.random.randint(minz, maxz)

        towerBase = TowerBase(
            origin = ivec3(x, center.y, z),
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
        sign = -1 if district in ['mm', 'mp'] else 1
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
        wallHeight = 25,
        width = 10,
        pillarRadius = 3
    )
    castleRoof = CastleRoof(
        origin = center + Y * (castleOutline.wallHeight+1),
        corners = castleOutline.corners,
        roofMaterial = TintedGlass,
        coneColors = {'mm': 'blue', 'mp': 'yellow', 'pp': 'green', 'pm': 'red'},
        height = 8,
        coneHeight = 3
    )
    castle = Castle(
        outline = castleOutline,
        roof = castleRoof
    )

    castle.place(editor)

    return castle


def buildBigTree(editor: Editor, center: ivec3) -> BigTree:
    """
    Place the big tree in the center of the build area.
    Returns the tree.
    """

    bigTree = BigTree(
        origin = center + Y,
        maxTrunkHeight = 20
    )

    bigTree.place(editor)

    return bigTree


def buildBridges(editor: Editor, towers: dict[str, Tower]) -> list[Bridge]:
    """
    Place the bridges between the towers.
    Returns a list of the bridges.
    """

    bridges = []
    
    basePalette = BasePalette()
    baseStairPalette = BaseStairPalette()
    noRoof = np.random.randint(0, 4)

    mm, mp, pp, pm = towers.values()
    for i, towerSet in enumerate([(mm, mp), (mm, pm), (mp, pp), (pm, pp)]):
        bridge = Bridge(
            towers = towerSet,
            baseMaterial = basePalette,
            stairMaterial = baseStairPalette,
            hasRoof = False if i == noRoof else True
        )
        bridge.place(editor)
        bridges.append(bridge)
    
    return bridges
