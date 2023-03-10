#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

import numpy as np

from gdpc import Block, geometry, Editor
from gdpc.minecraft_tools import signBlock
from glm import ivec3


class Tower:

    def __init__(
            self,
            editor: Editor,
            origin: ivec3,
            material: Block | list[Block],
            heights: list[int],
            radii: list[int],
            district: str
        ) -> None:

        assert len(heights) == len(radii) == 2
        assert district in ['mm', 'mp', 'pp', 'pm']

        self.editor = editor
        self.origin = origin
        self.material = material
        self.heights = heights
        self.radii = radii
        self.district = district
        return

    def build(self) -> None:
        for i in range(2):
            height, radius = self.heights[i], self.radii[i]
            baseY = 0 if i == 0 else self.heights[0]
            geometry.placeFittingCylinder(
                self.editor,
                self.origin + ivec3(-radius, baseY, -radius),
                self.origin + ivec3(radius, baseY + height, radius),
                self.material,
                tube = not i,
                hollow = i
            )
        # add signpost on top of tower with district name
        self.placeSign(self.origin + ivec3(0, sum(self.heights)+1, 0), self.district.upper())
        self.addEntrances()
        self.buildRoof()


    def buildRoof(self) -> None:
        # flat roof
        r = self.radii[1] + 3
        geometry.placeFittingCylinder(
            self.editor,
            self.origin + ivec3(-r, sum(self.heights), -r),
            self.origin + ivec3(r, sum(self.heights), r),
            self.material,
        )

        # edges
        r = self.radii[1] + 3
        geometry.placeFittingCylinder(
            self.editor,
            self.origin + ivec3(-r, sum(self.heights), -r),
            self.origin + ivec3(r, sum(self.heights)+2, r),
            self.material,
            tube = True
        )

        # pointy roof
        base = self.radii[1] - 1
        for r in range(base, 0, -1):
            y = sum(self.heights) + 1 + base - r
            geometry.placeFittingCylinder(
                self.editor,
                self.origin + ivec3(-r, y, -r),
                self.origin + ivec3(r, y, r),
                Block('crying_obsidian')
            )
            if r > 1:
                geometry.placeFittingCylinder(
                    self.editor,
                    self.origin + ivec3(-r+2, y, -r+2),
                    self.origin + ivec3(r-2, y, r-2),
                    Block('air')
                )

        # place purple stained glass at the top of the tower
        self.editor.placeBlock(
            self.origin + ivec3(0, y, 0),
            Block('purple_stained_glass')
        )

        # place pyramid of netherite blocks on top of the tower
        y = sum(self.heights) + 1
        for r in range(4, 0, -1):
            # rectangle
            geometry.placeCuboid(
                self.editor,
                self.origin + ivec3(-r, y, -r),
                self.origin + ivec3(r, y, r),
                Block('netherite_block')
            )
            y += 1
        # place beacon on top
        self.editor.placeBlock(
            self.origin + ivec3(0, y, 0),
            Block('beacon')
        )
    
    def hollow(self) -> None:
        geometry.placeFittingCylinder(
            self.editor,
            self.origin + ivec3(-self.radii[1]+1, self.heights[0]+1, -self.radii[1]+1),
            self.origin + ivec3(self.radii[1]-1, self.heights[0] + self.heights[1]-1, self.radii[1]-1),
            Block('air')
        )
    
    def placeSign(self, pos, label) -> None:
        self.editor.placeBlock(
            pos,
            signBlock(
            'oak', wall = False, rotation = 1,
            line2 = label, color = "orange", isGlowing = True
            )
        )

    @property
    def entranceDirections(self) -> list[str]:
        return {
            'mm': ['pz', 'px'],
            'mp': ['mz', 'px'],
            'pp': ['mz', 'mx'],
            'pm': ['pz', 'mx']
        }[self.district]

    def addEntrances(self) -> None:
        """ Add entrances to the tower. """
        for direction in ['pz', 'mz', 'px', 'mx']:
            if direction in self.entranceDirections:
                entrancePos: ivec3 = self._addEntrance(direction)
                setattr(self, f'entrance{direction.upper()}', entrancePos)
            else:
                setattr(self, f'entrance{direction.upper()}', None)

    def _addEntrance(self, direction: str) -> ivec3:
        """
        Helper method for addEntrances.
        Adds an entrance to the tower and returns the position of the entrance.
        """

        bottom, top, r = self.heights[0]+1, self.heights[0]+4, self.radii[1]
        
        def _placeEntrance(x1: int, x2: int, z1: int, z2: int) -> None:
            """ Adds an entrance to the tower. """

            geometry.placeCuboid(
                self.editor,
                self.origin + ivec3(x1, bottom, z1),
                self.origin + ivec3(x2, top, z2),
                Block('air')
            )
        
        if direction == 'pz':
            _placeEntrance(-1, 1, r-1, r)
            return self.origin + ivec3(0, bottom-1, r)
        elif direction == 'mz':
            _placeEntrance(-1, 1, -r, -r+1)
            return self.origin + ivec3(0, bottom-1, -r)
        elif direction == 'px':
            _placeEntrance(r-1, r, -1, 1)
            return self.origin + ivec3(r, bottom-1, 0)
        elif direction == 'mx':
            _placeEntrance(-r, -r+1, -1, 1)
            return self.origin + ivec3(-r, bottom-1, 0)
        else:
            raise ValueError(f'Invalid direction: {direction}')

class SuperTree:

    def __init__(
            self,
            editor: Editor,
            origin: ivec3,
            trunkHeight: int
        ) -> None:
        self.editor = editor
        self.origin = origin
        self.trunkHeight = trunkHeight

        self.build()

    def build(self) -> None:
        self.buildLeaves()
        self.buildTrunk()
    
    def buildTrunk(self) -> None:
        
        r = 2
        slice_ = np.ones((r*2+1, r*2+1))

        dropRate = 0.8
        for y in range(0, self.trunkHeight):

            # build the slice
            for x in range(-r, r+1):
                for z in range(-r, r+1):
                    if slice_[x+r, z+r]:
                        self.editor.placeBlock(
                            self.origin + ivec3(x, y, z),
                            Block('spruce_log', {'axis': 'y'})
                        )
            # if more than one block is left, maybe drop one
            if np.sum(slice_) > 1:
                if np.random.rand() < 1 - dropRate:
                    # check which indices that are True are the furthest away from the center (2,2)
                    furthestIndices = np.argwhere(slice_ == True)
                    furthestIndices = furthestIndices[np.argmax(np.linalg.norm(furthestIndices - (r, r), axis=1))]
                    # if it is a single index, set it to False
                    if furthestIndices.shape == (2,):
                        slice_[furthestIndices[0], furthestIndices[1]] = False
                    # if it is a list of indices, choose one of them randomly and set it to False
                    else:
                        furthestIndices = furthestIndices[np.random.randint(len(furthestIndices))]
                        slice_[furthestIndices[0], furthestIndices[1]] = False
                    
                dropRate **= 2

    def buildLeaves(self) -> None:

        for x in range(-7, 8):
            for z in range(-7, 8):
                for y in range(self.trunkHeight-14, self.trunkHeight+3):
                    # if the xz distance from the center is less than 7, place a leaf block
                    if np.linalg.norm(np.array([x, z])) < 7:
                        self.editor.placeBlock(
                            self.origin + ivec3(x, y, z),
                            Block('spruce_leaves')
                        )

    def buildBeacon(self) -> None:
        
        # place 3x3 beacon platform with diamond at y = -1
        for x in range(-1, 2):
            for z in range(-1, 2):
                self.editor.placeBlock(
                    self.origin + ivec3(x, -1, z),
                    Block('block_of_diamond')
                )

        self.editor.placeBlock(self.origin, Block('beacon'))
