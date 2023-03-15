#!/usr/bin/env python3

"""
All castle-related classes are defined here.
"""

from typing import Generator, Sequence

import numpy as np

from gdpc import Block, Editor
from gdpc.vector_tools import Y
from gdpc.minecraft_tools import signBlock
from glm import ivec3

from generators import fittingCylinder, cuboid3D, line3D, pyramid, cone
from materials import Air, Glass, Netherite, Water, Lava, Beacon, Magma, EndStoneBricks, EndStoneBrickWall, SpruceLog, SpruceLeaves, GlowStone


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
        editor.placeBlock(self.coneBasesG, self.baseM)
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
    def basementFloorG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the basement floor. """
        return cuboid3D(
            self.o + ivec3(-self.width, -self.basementHeight, -self.width),
            self.o + ivec3(+self.width, -self.basementHeight, +self.width)
        )
    
    @property
    def roofG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the roof. """
        return cuboid3D(
            self.o + ivec3(-self.width, self.wallHeight, -self.width),
            self.o + ivec3(+self.width, self.wallHeight, +self.width)
        )
    
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
    def coneBasesG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the cone base. """
        for cornerPos in self.corners.values():
            yield from fittingCylinder(
                cornerPos + ivec3(-4, self.wallHeight + 1, -4),
                cornerPos + ivec3(+4, self.wallHeight + 1, +4)
            )
        return

    @property
    def wallsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the walls. """
        for i, currentCornerPos in enumerate(self.corners.values()):
            if i == 3:
                nextCornerPos = self.corners[list(self.corners.keys())[0]]
            else:
                nextCornerPos = self.corners[list(self.corners.keys())[i+1]]
            yield from cuboid3D(
                currentCornerPos - Y * self.basementHeight,
                nextCornerPos + Y * self.wallHeight
            )
        return

    @property
    def hollowOutG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the hollow out. """
        w, wH, bH = self.width, self.wallHeight, self.basementHeight
        yield from cuboid3D(
            self.o + ivec3(-w + 1,    +1, -w + 1),
            self.o + ivec3(+w - 1, wH -1, +w - 1)
        )
        yield from cuboid3D(
            self.o + ivec3(-w + 1, -bH + 1, -w + 1),
            self.o + ivec3(+w - 1,      -1, +w - 1)
        )
        yield from cuboid3D(
            self.o + ivec3(-w + 3, wH, -w + 3),
            self.o + ivec3(+w - 3, wH, +w - 3)
        )
        return
    
    @property
    def corners(self) -> dict[str, ivec3]:
        """ Get the corners' coordinates. """
        w = self.width
        return {
            'nw': self.o + ivec3(-w, 0, -w),
            'sw': self.o + ivec3(-w, 0, +w),
            'se': self.o + ivec3(+w, 0, +w),
            'ne': self.o + ivec3(+w, 0, -w)
        }


class CastleBasement:
    """ A hidden basement with a beacon and a chest. """

    def __init__(self,
            origin: ivec3,
            baseMaterial: Block | list[Block],
            beaconColor: str, width: int
        ) -> None:
        """
        origin: reference point (center of the base)
        baseMaterial: will be used for most blocks
        beaconColor: color of the beacon
        width: width of the castle basement
        """
        self.o = origin
        self.baseM = baseMaterial
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
        editor.placeBlock(self.parkourBaseBlocksG, EndStoneBricks)
        editor.placeBlock(self.parkourWallBlocksG, EndStoneBrickWall)
        editor.placeBlock(self.o + ivec3(8, 5, -9), self.chest)
        editor.placeBlock(self.o + ivec3(8, 5, -8), self.textSign)
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
    def landingStructureG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the landing structure. """
        return cuboid3D(
            self.o + ivec3(-1, 1, -1),
            self.o + ivec3(+1, 5, +1)
        )
    
    @property
    def parkourBaseBlocksG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the parkour base blocks. """
        for x in range(3, 8, 2):
            yield(self.o + ivec3(x, 1, 0))
        yield self.o + ivec3(7, 1, -7)
        yield from cuboid3D(
            self.o + ivec3(7, 4, -7),
            self.o + ivec3(9, 4, -9)
        )
        return
    
    @property
    def parkourWallBlocksG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the parkour wall blocks. """
        for x in range(3, 8, 2):
            for y in range(2, 6):
                if x == 7 and y == 5:
                    continue
                yield(self.o + ivec3(x, y, 0))
        for z in range(0, -5, -2):
            yield(self.o + ivec3(9, 4, z))
        yield self.o + ivec3(9, 5, -5)
        yield self.o + ivec3(7, 2, -7)
        yield self.o + ivec3(7, 3, -7)
        yield self.o + ivec3(8, 5, -7)
        yield from line3D(
            self.o + ivec3(7, 5, -7),
            self.o + ivec3(7, 5, -9)
        )
        return
    
    @property
    def chest(self) -> Block:
        """ The chest block with items inside. """
        answer = f'{42:09b}'
        items = []
        for i in range(9):
            item = 'water_bucket' if int(answer[i]) else 'bucket'
            items.append(f'{{Slot:{9+i}b,id:"{item}",Count:1b}}')
        return Block('chest', {'facing': 'east'}, data = '{Items:[' + ','.join(items) + ']}')

    @property
    def textSign(self) -> Block:
        """ The final text sign. """
        return signBlock(
            wood = 'spruce', rotation = 11,
            line2 = 'THE ANSWER IS', line3 = '(obviously)',
            color = 'black', isGlowing = True
        )

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
    def conesG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the cones. """
        for corner in self.corners.values():
            yield from cone(ivec3(corner.x, self.o.y + 1, corner.z), 4)
        return


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
    def pedestalCutoutG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the pedestal cutout. """
        for x, z in [(-1, -1), (-1, +1), (+1, -1), (+1, +1), (0, 0)]:
            yield from line3D(
                self.o + ivec3(self.r * x, -3, self.r * z),
                self.o + ivec3(self.r * x, -1, self.r * z)
            )
        return

    @property
    def leavesG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the leaves. """
        return fittingCylinder(
            self.o + ivec3(-8, self.trunkHeight-9, -8),
            self.o + ivec3(+8, self.trunkHeight+5, +8)
        )

    @property
    def trunkG(self) -> Generator[ivec3, None, None]:
        """ Generator for the trunk. """
        yield from [
            self.o + ivec3(x-self.r, y, z-self.r)
            for y in range(self.trunkHeight) for x in range(self.d) for z in range(self.d)
            if self.trunkA[y, x, z]
        ]
        return
    
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
        w, h = self.outline.width, self.outline.wallHeight
        yield from [
            p for p in cuboid3D(
                self.o + ivec3(-w+1, 1, -w+1),
                self.o + ivec3(+w-1, 1, +w-1)
            ) if np.random.rand() < .5
        ]
        for x, z in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            yield self.o + ivec3(x * (w-1), h-1, z * (w-1))
            yield self.o + ivec3(x * (w+1), h-1, z * (w+1))
        return


class CastleEntrance:
    """ An entrance to the castle from the roof of a tower. """

    def __init__(self, origin: ivec3, district: str, material: Block | Sequence[Block]) -> None:
        """
        origin: the origin of the entrance
        district: the district of the castle's corner in which the entrance should be
        material: the material of the blocks making up the entrance
        """
        self.o = origin
        self.material = material
        self.district = district
        return

    def place(self, editor: Editor) -> None:
        """ Place the entrance in the Minecraft. """
        editor.placeBlock(self.platformsG, self.material)
        editor.placeBlock(self.lavaGuardG, self.material)
        editor.placeBlock(self.markingG, Magma)
        editor.placeBlock(self.cutoutsG, Air)
        editor.placeBlock(self.poleG, Magma)
        editor.placeBlock(self.o + ivec3(self.xSign * 2, 1, self.zSign * 2), self.textSign)
        return

    @property
    def xSign(self) -> int:
        """ The sign of the x coordinate of the entrance. """
        return {'w': +1, 'e': -1}[self.district[1]]
    
    @property
    def zSign(self) -> int:
        """ The sign of the z coordinate of the entrance. """
        return {'n': +1, 's': -1}[self.district[0]]

    @property
    def platformsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the platforms. """
        yield from fittingCylinder(
            self.o + ivec3(-3, 0, -3),
            self.o + ivec3(+3, 0, +3)
        )
        yield from fittingCylinder(
            self.o + ivec3(-3, 4, -3),
            self.o + ivec3(+3, 4, +3)
        )
        return
    
    @property
    def lavaGuardG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the lava guard. """
        return fittingCylinder(
            self.o + ivec3(-3, 5, -3),
            self.o + ivec3(+3, 5, +3),
            tube = True
        )

    @property
    def markingG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the marking. """
        yield from line3D(
            self.o + ivec3(self.xSign * -3, 0, self.zSign * -1),
            self.o + ivec3(self.xSign * -3, 4, self.zSign * -1)
        )
        yield from line3D(
            self.o + ivec3(self.xSign * -1, 0, self.zSign * -3),
            self.o + ivec3(self.xSign * -1, 4, self.zSign * -3)
        )
        yield self.o + ivec3(self.xSign * -2, 0, self.zSign * -2)
        yield self.o + ivec3(self.xSign * -2, 4, self.zSign * -2)
        return

    @property
    def cutoutsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the cutouts. """
        yield from line3D(
            self.o + ivec3(self.xSign * -2, 1, self.zSign * -2),
            self.o + ivec3(self.xSign * -2, 3, self.zSign * -2)
        )
        yield from cuboid3D(
            self.o + Y,
            self.o + ivec3(self.xSign * 2, 3, self.zSign * 2)
        )
        return
    
    @property
    def poleG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the pole in the middle. """
        return line3D(self.o + Y, self.o + 3 * Y)

    @property
    def textSign(self) -> str:
        """ A text sign with a hint. """
        rotation = {'sw': 2, 'nw': 6, 'ne': 10, 'se': 14}[self.district]
        return signBlock(
            wood = 'spruce', rotation = rotation,
            line1 = 'Look', line2 = 'for', line3 = 'the', line4 = 'Light',
            color = 'black', isGlowing = True
        )
