#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

import numpy as np

from gdpc import geometry, Editor, Box
from glm import ivec3
from gdpc.vector_tools import addY, Y, X

from structs.tower import Tower, TowerBase, TowerRoom, TowerRoof, TowerRoofAccess, TowerStairway
from structs.bridge import Bridge
from structs.castle import Castle, CastleOutline, CastleBasement, CastleRoof, CastleTree, CastleEntrance
from structs.interior import ExoticWoodInterior, NostalgicInterior, EndGameInterior
from generators import line3D
from materials import BasePalette, BaseStairPalette, Concrete, CryingObsidian, TintedGlass, signBlock
from helper import timer

@timer
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

    for (x, z), color, district in zip(directions, colors, ['NW', 'SW', 'SE', 'NE']):
        xz = center + ivec3(x * 50, 0, z * 50)
        editor.placeBlock(line3D(xz, xz + ivec3(0, 10, 0)), Concrete(color))
        editor.placeBlock(xz + ivec3(0, 11, 0), signBlock('birch', facing='north', line2=district))


@timer
def buildTowers(editor: Editor, center: ivec3, heightMap: np.ndarray) -> dict[str, Tower]:
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
    interiorTypes = ['nostalgic', 'crimson', 'warped', 'endgame']
    while True:
        # shuffle until nostalgic and endgame differ by exactly 2 indices
        np.random.shuffle(interiorTypes)
        if np.abs(interiorTypes.index('nostalgic') - interiorTypes.index('endgame')) == 2:
            break
    
    for (minx, minz, maxx, maxz), district, interiorType in zip(bounds, towers.keys(), interiorTypes):
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
            interiorType = interiorType,
            base = towerBase,
            room = towerRoom,
            roof = towerRoof,
            roofAccess = towerRoofAccess
        )

        tower.place(editor)
        maxHeight = towerBase.extend(editor, heightMap, center)
        tower.extensionHeight = maxHeight
        towers[district] = tower

    return towers


@timer
def buildCastle(editor: Editor, relativeCenter: ivec3, absoluteCenter: ivec3, heightMap: np.ndarray) -> Castle:
    """
    Place the castle in the center of the towers.
    Returns the castle.
    """

    basePalette = BasePalette()

    castleOutline = CastleOutline(
        origin = relativeCenter,
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
        origin = relativeCenter + Y * (castleOutline.wallHeight+1),
        corners = castleOutline.corners,
        roofMaterial = TintedGlass,
        height = 8
    )
    castleTree = CastleTree(
        origin = relativeCenter + Y,
        maxTrunkHeight = 20
    )
    castle = Castle(
        outline = castleOutline,
        basement = castleBasement,
        roof = castleRoof,
        tree = castleTree
    )

    castle.place(editor)
    castle.outline.extend(editor, heightMap, absoluteCenter)

    return castle


@timer
def buildBridges(editor: Editor, towers: dict[str, Tower]) -> None:
    """ Place the bridges between the towers. """
    
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
    
    return


@timer
def buildEntryPoints(editor: Editor, castle: Castle, towers: dict[str, Tower]) -> None:
    """
    Place a stairway around the tower with the nostalgic interior.
    On the opposite district, the castle entrance will be placed.
    """

    tower = [t for t in towers.values() if t.interiorType == 'nostalgic'][0]
    dT = tower.district
    levels = (tower.base.height + tower.extensionHeight) // 5
    towerStairway = TowerStairway(
        towerBase = tower.base,
        material = BaseStairPalette(),
        levels = levels
    )
    towerStairway.place(editor)

    dC = {'nw': 'se', 'sw': 'ne', 'se': 'nw', 'ne': 'sw'}[dT]

    castleEntrance = CastleEntrance(
        origin = castle.outline.corners[dC] + 20 * Y,
        district = dC,
        material = BasePalette()
    )
    castleEntrance.place(editor)

    return


@timer
def buildInteriors(editor: Editor, towers: dict[str, Tower]) -> None:
    """ Place the interiors of the towers. """

    for tower in towers.values():
        if tower.interiorType == 'nostalgic':
            interior = NostalgicInterior(tower)
        elif tower.interiorType == 'crimson':
            interior = ExoticWoodInterior(tower, 'crimson')
        elif tower.interiorType == 'warped':
            interior = ExoticWoodInterior(tower, 'warped')
        elif tower.interiorType == 'endgame':
            interior = EndGameInterior(tower)
        interior.place(editor)
    return
