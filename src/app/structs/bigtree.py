#!/usr/bin/env python3

"""
The big tree class is defined here.
"""

import numpy as np

from gdpc import Editor
from glm import ivec3

from generators import cuboid3D
from materials import Diamond, Beacon, SpruceLeaves, SpruceLog


class BigTree:

    def __init__(self,
            origin: ivec3, maxTrunkHeight: int
        ) -> None:
        """
        origin: reference point for the tree (beacon will be placed here)
        maxTrunkHeight: the maximum height of the trunk
        """

        self.o = origin
        self.maxTrunkHeight = maxTrunkHeight
        self.trunkHeight = 0
        self.r = 2
        self.d = self.r*2+1
        self.trunk: np.ndarray = np.empty((self.maxTrunkHeight, self.d, self.d), dtype=bool)

        self._setTrunk()
        self._setLeaves()

    def place(self, editor: Editor) -> None:
        editor.placeBlock(self.leavesGenerator, SpruceLeaves)
        editor.placeBlock(self.trunkGenerator, SpruceLog)
        editor.placeBlock(
            cuboid3D(
                corner1 = self.o + ivec3(-1, -1, -1),
                corner2 = self.o + ivec3(+1, -1, +1)
            ),
            Diamond
        )
        editor.placeBlock(self.o, Beacon)


    def _setTrunk(self) -> None:
        """ Construct the trunk of the tree as a 2D numpy array. """

        # initialize slice with all True
        slice_: np.ndarray = np.ones((self.d, self.d), dtype=bool)
        # set middle to False
        slice_[self.r, self.r] = False
        # set corners to False
        for x, z in [(0, 0), (0, self.d-1), (self.d-1, 0), (self.d-1, self.d-1)]:
            slice_[x, z] = False

        # drop rate will determine the rate at which a block is dropped
        # at each iteration (we build from bottom up)
        dropRate = 0.75
        for y in range(self.maxTrunkHeight):
            # if there's no blocks left, break
            if np.sum(slice_) == 1:
                break
            # if there are, maybe drop one
            if np.random.rand() < 1 - dropRate:
                # check which indices that are True are the furthest away from the center (self.r, self.r)
                furthestIndices = np.argwhere(slice_ == True)
                furthestIndices = furthestIndices[np.argmax(np.linalg.norm(furthestIndices - (self.r, self.r), axis=1))]
                # if it is a single index, set it to False
                if furthestIndices.shape == (2,):
                    slice_[furthestIndices[0], furthestIndices[1]] = False
                # if it is a list of indices, choose one of them randomly and set it to False
                else:
                    furthestIndices = furthestIndices[np.random.randint(len(furthestIndices))]
                    slice_[furthestIndices[0], furthestIndices[1]] = False
                
            dropRate **= 2
            # add the slice to trunk object at level y
            self.trunk[y] = slice_
    
        # set the final trunk height
        self.trunkHeight = y

        # construct the generator (point sequence) for the trunk
        r = self.r
        self.trunkGenerator = []
        for y in range(0, self.trunkHeight+1):
            for x in range(-r, r+1):
                for z in range(-r, r+1):
                    if self.trunk[y, x+r, z+r]:
                        self.trunkGenerator.append(self.o + ivec3(x, y, z))
    

    def _setLeaves(self) -> None:
        """ Construct a leaves generator (point sequence). """

        self.leavesGenerator = []
        for x in range(-8, 9):
            for z in range(-8, 9):
                for y in range(self.trunkHeight-10, self.trunkHeight+3):
                    # if the xz distance from the center is less than 7, place a leaf block
                    if np.linalg.norm(np.array([x, z])) < 7:
                        self.leavesGenerator.append(self.o + ivec3(x, y, z))
