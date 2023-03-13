#!/usr/bin/env python3

"""
All castle-related classes are defined here.
"""

from typing import Generator, Sequence

import numpy as np

from gdpc import Block, Editor
from gdpc.vector_tools import Y
from glm import ivec3

from generators import fittingCylinder, cuboid3D, line3D, pyramid, cone
from materials import Air, Glass, Netherite, Water, Lava, Beacon, Magma, EndStoneBricks, SpruceLog, SpruceLeaves


class CastleOutline:

    def __init__(self,
            origin: ivec3,
            baseMaterial: Block | Sequence[Block],
            wallHeight: int, basementHeight: int, width: int
        ) -> None:
        """
        origin: reference point (center of the base)
        baseMaterial: will be used for most blocks
        wallHeight: height of the walls (excluding the roof) from origin
        basementHeight: height of the basement (excluding the base) to origin
        width: nr. of blocks that the walls are removed from the center
        """
        self.o = origin
        self.baseM = baseMaterial
        self.wallHeight = wallHeight
        self.basementHeight = basementHeight
        self.width = width
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the castle outline in minecraft """
        editor.placeBlock(self.mainFloorG, self.baseM)
        editor.placeBlock(self.basementFloorG, self.baseM)
        editor.placeBlock(self.roofG, self.baseM)
        editor.placeBlock(self.cornerPillarsG, self.baseM)
        editor.placeBlock(self.wallsG, self.baseM)
        editor.placeBlock(self.hollowOutG, Air)
        return

    @property
    def mainFloorG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the main floor. """
        return cuboid3D(
            self.o + ivec3(-self.width, 0, -self.width),
            self.o + ivec3(+self.width, 0, +self.width)
        )
    @property
    def mainfloorPC(self) -> Sequence[ivec3]:
        """ Positions of the main floor. """
        return list(self.mainFloorG)
    
    @property
    def basementFloorG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the basement floor. """
        return cuboid3D(
            self.o + ivec3(-self.width, -self.basementHeight, -self.width),
            self.o + ivec3(+self.width, -self.basementHeight, +self.width)
        )
    @property
    def basementFloorPC(self) -> Sequence[ivec3]:
        """ Positions of the basement floor. """
        return list(self.basementFloorG)
    
    @property
    def roofG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the roof. """
        return cuboid3D(
            self.o + ivec3(-self.width, self.wallHeight, -self.width),
            self.o + ivec3(+self.width, self.wallHeight, +self.width)
        )
    @property
    def roofPC(self) -> Sequence[ivec3]:
        """ Positions of the roof. """
        return list(self.roofG)
    
    @property
    def cornerPillarsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the corner pillars. """
        for cornerPos in self.corners.values():
            yield from fittingCylinder(
                cornerPos + ivec3(-3, -self.basementHeight, -3),
                cornerPos + ivec3(+3, +self.wallHeight,     +3),
                hollow = True
            )
        return
    @property
    def cornerPillarsPC(self) -> Sequence[ivec3]:
        """ Positions of the corner pillars. """
        return list(self.cornerPillarsG)

    @property
    def wallsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the walls. """
        for i, currentCornerPos in enumerate(self.corners.values()):
            try:
                nextCornerPos = self.corners[list(self.corners.keys())[i+1]]
            except IndexError:
                nextCornerPos = self.corners[list(self.corners.keys())[0]]
            yield from cuboid3D(
                currentCornerPos - Y * self.basementHeight,
                nextCornerPos + Y * self.wallHeight
            )
        return
    @property
    def wallsPC(self) -> Sequence[ivec3]:
        """ Positions of the walls. """
        return list(self.wallsG)

    @property
    def hollowOutG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the hollow out. """
        yield from cuboid3D(
            self.o + ivec3(-self.width + 1,                +1, -self.width + 1),
            self.o + ivec3(+self.width - 1, self.wallHeight-1, +self.width - 1)
        )
        yield from cuboid3D(
            self.o + ivec3(-self.width + 1, -self.basementHeight+1, -self.width + 1),
            self.o + ivec3(+self.width - 1,                     -1, +self.width - 1)
        )
        yield from cuboid3D(
            self.o + ivec3(-self.width + 3, self.wallHeight, -self.width + 3),
            self.o + ivec3(+self.width - 3, self.wallHeight, +self.width - 3)
        )
        return
    @property
    def hollowOutPC(self) -> Sequence[ivec3]:
        """ Positions of the hollow out. """
        return list(self.hollowOutG)
    
    @property
    def corners(self) -> dict[str, ivec3]:
        """ Get the corners' coordinates. """
        return {
            'nw': self.o + ivec3(-self.width, 0, -self.width),
            'sw': self.o + ivec3(-self.width, 0, +self.width),
            'se': self.o + ivec3(+self.width, 0, +self.width),
            'ne': self.o + ivec3(+self.width, 0, -self.width)
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
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the castle basement in minecraft """
        editor.placeBlock(self.lavaG, Lava)
        editor.placeBlock(self.landingStructureG, Netherite)
        editor.placeBlock(self.o + 2 * Y, Beacon)
        editor.placeBlock(self.o + 3 * Y, Block(f'{self.beaconColor}_stained_glass_pane'))
        editor.placeBlock(self.o + 4 * Y, Air)
        editor.placeBlock(self.o + 5 * Y, Water)
        return

    @property
    def lavaG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the lava. """
        yield from [
            p for p in cuboid3D(
                self.o + ivec3(-self.width+1, 1, -self.width+1),
                self.o + ivec3(+self.width-1, 1, +self.width-1)
            ) if np.random.rand() < .5
        ]
        return
    @property
    def lavaPC(self) -> Sequence[ivec3]:
        """ Positions of the lava. """
        return list(self.lavaG)

    @property
    def landingStructureG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the landing structure. """
        return cuboid3D(
            self.o + ivec3(-1, 1, -1),
            self.o + ivec3(+1, 5, +1)
        )
    @property
    def landingStructurePC(self) -> Sequence[ivec3]:
        """ Positions of the landing structure. """
        return list(self.landingStructureG)


class CastleRoof:

    def __init__(self,
            origin: ivec3, corners: dict[str, ivec3],
            roofMaterial: Block | list[Block], height: int
        ) -> None:
        """
        origin: reference point (center of the roof)
        corners: dict with the corners' coordinates
        roofMaterial: will be used for the roof
        height: height of the pyramid roof from origin
        """
        self.o = origin
        self.corners = corners
        self.roofM = roofMaterial
        self.height = height
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the castle roof in minecraft """
        editor.placeBlock(self.roofPyramidG, self.roofM)
        editor.placeBlock(self.conesG, Magma)
        editor.placeBlock(self.o + Y * (self.height-1), Air)
        editor.placeBlock(self.o + Y * (self.height-2), Glass)
        return

    @property
    def roofPyramidG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the roof pyramid. """
        return pyramid(self.o, self.height, True)
    @property
    def roofPyramidPC(self) -> Sequence[ivec3]:
        """ Positions of the roof pyramid. """
        return list(self.roofPyramidG)
    
    @property
    def conesG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the cones. """
        for corner in self.corners.values():
            yield from cone(ivec3(corner.x, self.o.y, corner.z), 3)
        return
    @property
    def conesPC(self) -> Sequence[ivec3]:
        """ Positions of the cones. """
        return list(self.conesG)


class CastleTree:

    def __init__(self, origin: ivec3, maxTrunkHeight: int) -> None:
        """
        origin: origin of the pedestal
        maxTrunkHeight: the maximum height of the trunk

        ! Note: bigTree.o will be set to the origin of the tree, not the pedestal !
        """

        self.o = origin + 3 * Y
        self.maxTrunkHeight = maxTrunkHeight
        self.trunkHeight = 0
        self.r = 2
        self.d = self.r*2+1
        self._constructTrunk()

    def _constructTrunk(self):
        """ Construct the trunk of the tree as a 3D numpy array. """
        self.trunkA = np.zeros((self.maxTrunkHeight, self.d, self.d), dtype=bool)
        
        slice_: np.ndarray = np.ones((self.d, self.d), dtype=bool)
        slice_[self.r, self.r] = False
        d = self.d
        for x, z in [(0, 0), (0, d-1), (d-1, 0), (d-1, d-1)]:
            slice_[x, z] = False

        dropRate = 0.99
        for y in range(self.maxTrunkHeight):
            self.trunkA[y] = slice_
            self.trunkHeight = y
            if np.sum(slice_) == 1:
                break
            if np.random.rand() < dropRate:
                x, z = self.furthestIndex(slice_)
                slice_[x, z] = False
                dropRate *= dropRate

    def place(self, editor: Editor) -> None:
        """ Place the tree in the Minecraft. """
        editor.placeBlock(self.pedestalG, EndStoneBricks)
        editor.placeBlock(self.pedestalCutoutG, Air)
        editor.placeBlock(self.leavesG, SpruceLeaves)
        editor.placeBlock(self.trunkG, SpruceLog)

    @property
    def pedestalG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the pedestal. """
        return cuboid3D(
            self.o + ivec3(-self.r, -3, -self.r),
            self.o + ivec3(+self.r, -1, +self.r)
        )
    @property
    def pedestalPC(self) -> Sequence[ivec3]:
        """ Positions the pedestal. """
        return list(self.pedestalG)
    
    @property
    def pedestalCutoutG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the pedestal cutout. """
        for x, z in [(-1, -1), (-1, +1), (+1, -1), (+1, +1), (0, 0)]:
            yield from line3D(
                self.o + ivec3(self.r * x, -3, self.r * z),
                self.o + ivec3(self.r * x, -1, self.r * z)
            )
        return
    @property
    def pedestalCutoutPC(self) -> Sequence[ivec3]:
        """ Positions the pedestal cutout. """
        return list(self.pedestalCutoutG)

    @property
    def leavesG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the leaves. """
        return fittingCylinder(
            self.o + ivec3(-8, self.trunkHeight-9, -8),
            self.o + ivec3(+8, self.trunkHeight+5, +8)
        )
    @property
    def leavesPC(self) -> Sequence[ivec3]:
        """ Positions the leaves. """
        return list(self.leavesG)

    @property
    def trunkG(self) -> Generator[ivec3, None, None]:
        """ Generator for the trunk. """
        yield from [
            self.o + ivec3(x-self.r, y, z-self.r)
            for y in range(self.trunkHeight) for x in range(self.d) for z in range(self.d)
            if self.trunkA[y, x, z]
        ]
        return
    @property
    def trunkPC(self) -> Sequence[ivec3]:
        """ Positions the trunk. """
        return list(self.trunkG)
    
    def furthestIndex(self, A: np.ndarray) -> tuple[int, int]:
        """ Return the furthest index from the center of the trunk. """
        A = np.argwhere(A == True)
        A = A[np.argmax(np.linalg.norm(A - (self.r, self.r), axis=1))]
        if A.shape != (2,):
            A = A[np.random.randint(len(A))]
        return (A[0], A[1])


class Castle:
    """ The castle in the middle of the map. """

    def __init__(self,
            outline: CastleOutline, basement: CastleBasement, roof: CastleRoof,
            tree: CastleTree
        ) -> None:
        """
        outline: the castle outline
        basement: the castle basement
        roof: the castle roof
        tree: the tree in the middle of the castle
        
        ! Note: castle.o(rigin) is set to outline.o(rigin) !
        """
        self.o = outline.o
        self.outline = outline
        self.basement = basement
        self.roof = roof
        self.tree = tree
        return

    def place(self, editor: Editor) -> None:
        """ Place the castle in minecraft """
        self.outline.place(editor)
        self.basement.place(editor)
        self.roof.place(editor)
        editor.placeBlock(self.lavaG, Lava)
        self.tree.place(editor)
        editor.placeBlock(self.o, Air)
        return
    
    @property
    def lavaG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the lava on the main floor. """
        yield from [
            p for p in cuboid3D(
                self.o + ivec3(-self.outline.width+1, 1, -self.outline.width+1),
                self.o + ivec3(+self.outline.width-1, 1, +self.outline.width-1)
            ) if np.random.rand() < .5
        ]
        return
    @property
    def lavaPC(self) -> Sequence[ivec3]:
        """ Positions of the lava on the main floor. """
        return list(self.lavaG)
