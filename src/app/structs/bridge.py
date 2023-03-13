#!/usr/bin/env python3

"""
The bridge class is defined here.
"""

from typing import Generator, Sequence
import numpy as np

from gdpc import Block, Editor
from glm import ivec3

from generators import line3D
from .tower import Tower


class Bridge:
    """ A bridge connecting two towers. """

    def __init__(self,
            towers: tuple[Tower, Tower],
            baseMaterial: Block | Sequence[Block],
            stairMaterial: Block | Sequence[Block],
            hasRoof: bool
        ) -> None:
        """
        towers: a tuple of two Tower instances
        baseMaterial: the material of the bridge base
        stairMaterial: the material of the bridge stairs
        hasRoof: whether the bridge has a roof
        """

        assert len(towers) == 2, 'A bridge can only connect two towers.'
        self.towers = towers
        self.baseM = baseMaterial
        self.stairM = stairMaterial
        self.hasRoof = hasRoof
        self._setTowers()
        return
    
    def _setTowers(self) -> None:
        """ Set the two towers in correct order. """
        if self.direction == 'x':
            t1, t2 = sorted(self.towers, key=lambda t: t.o.x)
            self.from_, self.to_ = t1.entranceOrigins['x'], t2.entranceOrigins['x']
        elif self.direction == 'z':
            t1, t2 = sorted(self.towers, key=lambda t: t.o.z)
            self.from_, self.to_ = t1.entranceOrigins['z'], t2.entranceOrigins['z']
        else:
            raise ValueError(f'Invalid direction: {self.direction}')
        return

    def place(self, editor: Editor) -> None:
        """ Place the bridge in Minecraft. """
        editor.placeBlock(self.baseG, self.baseM)
        for i in range(4):
            self.stairM.setFacing(self.stairsDirections[i%2])
            self.stairM.setHalf('top')
            if i >= 2:
                self.stairM.setHalf('bottom')
            editor.placeBlock(self.stairsPC[i], self.stairM)
        return

    @property
    def baseG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the bridge base. """
        for a in self.walkRange:
            b = self._getB(a)
            yield self.p(a, b, -1)
            yield from line3D(self.p(a, b-2, 0), self.p(a, b+2, 0))
            yield from [self.p(a, b-2, 1), self.p(a, b+2, 1)]
            if self.hasRoof:
                yield from line3D(self.p(a, b-1, 4), self.p(a, b+1, 4))
                yield self.p(a, b, 5)
                if np.random.rand() < 0.5:
                    sign = np.random.choice([-1, 1])
                    yield from [self.p(a, b + sign*2, 2), self.p(a, b + sign*2, 3)]
        return
    @property
    def basePC(self) -> Sequence[ivec3]:
        """ Positions of the bridge base. """
        return list(self.baseG)
    
    @property
    def stairsPC(self) -> Sequence[Sequence[ivec3]]:
        """ Positions of the four sets of decorative stairs. """
        stairsPC = [[], [], [], []]
        for a in self.walkRange:
            b = self._getB(a)
            stairsPC[0].append(self.p(a, b-1, -1))
            stairsPC[1].append(self.p(a, b+1, -1))
            if self.hasRoof:
                stairsPC[2].extend([self.p(a, b-2, 4), self.p(a, b-1, 5)])
                stairsPC[3].extend([self.p(a, b+2, 4), self.p(a, b+1, 5)])
        return stairsPC

    def p(self, i: int, j: int, k: int) -> ivec3:
        """ helper method for switching between x and z directions """
        if self.direction == 'x':
            return ivec3(i, self.from_.y+k, j)
        else:
            return ivec3(j, self.from_.y+k, i)
    
    def _getB(self, a: int) -> int:
        """ helper method for getting the z coordinate of the bridge at a given x coordinate or vice versa. """
        if self.direction == 'x':
            return round(self.from_.z + (self.to_.z - self.from_.z) * (a - self.from_.x) / (self.to_.x - self.from_.x))
        else:
            return round(self.from_.x + (self.to_.x - self.from_.x) * (a - self.from_.z) / (self.to_.z - self.from_.z))
    
    @property
    def direction(self) -> str:
        """ The direction of the bridge, either 'x' or 'z'. """
        if self.towers[0].district[1] == self.towers[1].district[1]:
            return 'z'
        elif self.towers[0].district[0] == self.towers[1].district[0]:
            return 'x'
        else:
            raise ValueError(
                'Invalid combination of towers: ' +
                f'{self.towers[0].district}, {self.towers[1].district}'
            )
    
    @property
    def walkRange(self) -> range:
        """ Direction to loop over when determining point collections. """
        return {
            'x': range(self.from_.x+1, self.to_.x),
            'z': range(self.from_.z+1, self.to_.z)
        }[self.direction]

    @property
    def stairsDirections(self) -> tuple[str, str]:
        """ Get the directions of the stairs. """
        if self.direction == 'x':
            return ('south', 'north')
        else:
            return ('east', 'west')
