#!/usr/bin/env python3

"""
All castle-related classes are defined here.
"""

import numpy as np

from gdpc import Block, Editor
from gdpc.vector_tools import Y
from glm import ivec3

from generators import fittingCylinder, cuboid3D, pyramid, cone
from materials import Air, Glass, Netherite, Water, Lava, Beacon


class CastleOutline:

    def __init__(self,
            origin: ivec3,
            baseMaterial: Block | list[Block],
            wallHeight: int, basementHeight: int,
            width: int, pillarRadius: int
        ) -> None:
        """
        origin: reference point (center of the base)
        baseMaterial: will be used for most blocks
        wallHeight: height of the walls (excluding the roof) from origin
        basementHeight: height of the basement (excluding the base) to origin
        width: nr. of blocks that the walls are removed from the center
        pillarRadius: radius of the pillars
        """
        self.o = origin
        self.baseM = baseMaterial
        self.wallHeight = wallHeight
        self.basementHeight = basementHeight
        self.width = width
        self.pillarRadius = pillarRadius
        self._setGenerators()
    
    def place(self, editor: Editor) -> None:
        """ Place the castle outline in minecraft """
        for floorGenerator in [self.mainFloorGenerator, self.basementFloorGenerator]:
            editor.placeBlock(floorGenerator, self.baseM)
        for c in self.corners.keys():
            editor.placeBlock(self.cornerPillarGenerators[c], self.baseM)
            editor.placeBlock(self.wallGenerators[c], self.baseM)
        editor.placeBlock(self.roofGenerator, self.baseM)
        for hollowOutGenerator in [self.hollowOutGenerator1, self.hollowOutGenerator2, self.hollowOutGenerator3]:
            editor.placeBlock(hollowOutGenerator, Air)
        
        return

    def _setGenerators(self) -> None:
        """ Set the generators for the walls. """

        self.mainFloorGenerator = cuboid3D(
            corner1 = self.o + ivec3(-self.width, 0, -self.width),
            corner2 = self.o + ivec3(+self.width, 0, +self.width)
        )
        self.basementFloorGenerator = cuboid3D(
            corner1 = self.o + ivec3(-self.width, -self.basementHeight, -self.width),
            corner2 = self.o + ivec3(+self.width, -self.basementHeight, +self.width)
        )
        self.roofGenerator = cuboid3D(
            corner1 = self.o + ivec3(-self.width, self.wallHeight, -self.width),
            corner2 = self.o + ivec3(+self.width, self.wallHeight, +self.width)
        )
        # copy corner keys
        self.cornerPillarGenerators = self.corners.copy()
        self.wallGenerators = self.corners.copy()
        for i, (district, currentCornerPos) in enumerate(self.corners.items()):
            # the corner pillar will generate a pillar from the current corner to the top
            self.cornerPillarGenerators[district] = fittingCylinder(
                corner1 = currentCornerPos + ivec3(-self.pillarRadius, -self.basementHeight, -self.pillarRadius),
                corner2 = currentCornerPos + ivec3(+self.pillarRadius, +self.wallHeight,     +self.pillarRadius),
                hollow = True
            )
            # the cuboid will generate a wall from the current corner to the next corner
            try:
                self.wallGenerators[district] = cuboid3D(
                    corner1 = currentCornerPos - Y * self.basementHeight,
                    corner2 = self.corners[list(self.corners.keys())[i+1]] + Y * self.wallHeight
                )
            except IndexError:
                self.wallGenerators[district] = cuboid3D(
                    corner1 = currentCornerPos - Y * self.basementHeight,
                    corner2 = self.corners[list(self.corners.keys())[0]] + Y * self.wallHeight
                )
        # finally, we need to hollow out some stuff
        self.hollowOutGenerator1 = cuboid3D(
            corner1 = self.o + ivec3(-self.width + 1,                +1, -self.width + 1),
            corner2 = self.o + ivec3(+self.width - 1, self.wallHeight-1, +self.width - 1)
        )
        self.hollowOutGenerator2 = cuboid3D(
            corner1 = self.o + ivec3(-self.width + 1, -self.basementHeight+1, -self.width + 1),
            corner2 = self.o + ivec3(+self.width - 1,                     -1, +self.width - 1)
        )
        self.hollowOutGenerator3 = cuboid3D(
            corner1 = self.o + ivec3(-self.width + 3, self.wallHeight, -self.width + 3),
            corner2 = self.o + ivec3(+self.width - 3, self.wallHeight, +self.width - 3)
        )

        return
    
    @property
    def corners(self) -> dict[str, ivec3]:
        """ Get the corners' coordinates. """
        return {
            'mm': self.o + ivec3(-self.width, 0, -self.width),
            'mp': self.o + ivec3(-self.width, 0, +self.width),
            'pp': self.o + ivec3(+self.width, 0, +self.width),
            'pm': self.o + ivec3(+self.width, 0, -self.width)
        }


class CastleBasement:
    """ A hidden basement with a beacon and a chest. """

    def __init__(self,
            origin: ivec3,
            baseMaterial: Block | list[Block], chest: Block,
            beaconColor: str, width: int
        ) -> None:
        """
        origin: reference point (center of the base)
        baseMaterial: will be used for most blocks
        chest: chest block with the items
        beaconColor: color of the beacon
        width: width of the castle basement
        """
        self.o = origin
        self.baseM = baseMaterial
        self.chestBlock = chest
        self.beaconColor = beaconColor
        self.width = width
        self._setGenerators()
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the castle basement in minecraft """
        editor.placeBlock(self.lavaGenerator, Lava)
        editor.placeBlock(self.landingStructureGenerator, Netherite)
        editor.placeBlock(self.o + 2 * Y, Beacon)
        editor.placeBlock(self.o + 3 * Y, Block(f'{self.beaconColor}_stained_glass_pane'))
        editor.placeBlock(self.o + 4 * Y, Air)
        editor.placeBlock(self.o + 5 * Y, Water)
        return

    def _setGenerators(self) -> None:
        """ Set the generators for the basement. """

        # randomly generate lava on the floor (50% chance) for each block
        self.lavaGenerator = cuboid3D(
            corner1 = self.o + ivec3(-self.width+1, 1, -self.width+1),
            corner2 = self.o + ivec3(+self.width-1, 1, +self.width-1)
        )
        self.lavaGenerator = [p for p in self.lavaGenerator if np.random.rand() < .5]

        self.landingStructureGenerator = cuboid3D(
            corner1 = self.o + ivec3(-1, 1, -1),
            corner2 = self.o + ivec3(+1, 5, +1)
        )

        return

class CastleRoof:

    def __init__(self,
            origin: ivec3, corners: dict[str, ivec3],
            roofMaterial: Block | list[Block], coneColors: dict[str, str],
            height: int, coneHeight: int
        ) -> None:
        """
        origin: reference point (center of the roof)
        corners: dict with the corners' coordinates
        roofMaterial: will be used for the roof
        coneColors: dict with colors for the cones
        height: height of the pyramid roof from origin
        coneHeight: height of the cones
        """
        self.o = origin
        self.corners = corners
        self.roofM = roofMaterial
        self.coneColors = coneColors
        self.height = height
        self.coneHeight = coneHeight
        self._setGenerators()
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the castle roof in minecraft """
        editor.placeBlock(self.roofGenerator, self.roofM)
        for corner, color in self.coneColors.items():
            editor.placeBlock(self.coneGenerators[corner], Block('magma_block'))
        # place normal glass block at the very top
        editor.placeBlock(self.o + Y * (self.height-1), Air)
        editor.placeBlock(self.o + Y * (self.height-2), Glass)
        return

    def _setGenerators(self) -> None:
        """ Determine the locations of (almost) all blocks of the castle roof. """
        # the roof is a hollow pyramid of stained glass blocks
        self.roofGenerator = pyramid(self.o, self.height, True)
        self.coneGenerators = self.corners.copy()
        for corner, pos in self.corners.items():
            corner
            self.coneGenerators[corner] = cone(
                origin = ivec3(pos.x, self.o.y, pos.z),
                height = self.coneHeight,
            )
        return


class Castle:
    """ The castle in the middle of the map. """

    def __init__(self,
            outline: CastleOutline, basement: CastleBasement, roof: CastleRoof
        ) -> None:
        """
        outline: the castle outline
        basement: the castle basement
        roof: the castle roof
        
        ! Note: castle.o(rigin) is set to outline.o(rigin) !
        """
        self.outline = outline
        self.o = self.outline.o
        self.basement = basement
        self.roof = roof
        return

    def place(self, editor: Editor) -> None:
        """ Place the castle in minecraft """
        self.outline.place(editor)
        self.basement.place(editor)
        self.roof.place(editor)
        editor.placeBlock(self.o, Air)
        return
