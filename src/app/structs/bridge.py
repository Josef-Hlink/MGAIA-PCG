#!/usr/bin/env python3

"""
The bridge class is defined here.
"""

import numpy as np

from gdpc import Block, Editor
from glm import ivec3

from generators import line3D
from .tower import Tower


class Bridge:
    """ A bridge connecting two towers. """

    def __init__(self,
            towers: tuple[Tower, Tower],
            baseMaterial: Block, stairMaterial: Block,
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
        self._setGenerators()
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the bridge in Minecraft. """
        editor.placeBlock(self.basePoints, self.baseM)
        for i in range(4):
            self.stairM.setFacing(self.stairsDirections[i%2])
            if i == 2:
                # flip the stairs
                self.stairM.setHalf('top')
            editor.placeBlock(self.stairsPoints[i], self.stairM)
        return

    def _setGenerators(self) -> None:
        """ Set the generators (point sequences) for the bridge. """
        self.basePoints = []
        self.stairsPoints = [[], [], [], []]
        walkRange = range(self.from_.x+1, self.to_.x) if self.direction == 'x' else range(self.from_.z+1, self.to_.z)
        y = self.from_.y + 1

        def p(i: int, j: int, k: int) -> ivec3:
            """ helper method for switching between x and z directions """
            if self.direction == 'x':
                return ivec3(i, y+k, j)
            else:
                return ivec3(j, y+k, i)

        for a in walkRange:
            b = self._getB(a)
            # the "origin" of the bridge
            self.basePoints.append(p(a, b, 0))
            self.stairsPoints[2].append(p(a, b-1, 0))
            self.stairsPoints[3].append(p(a, b+1, 0))
            # walkable area
            self.basePoints.extend(line3D(
                begin = p(a, b-2, +1),
                end   = p(a, b+2, +1)
            ))
            # rails
            self.basePoints.extend([p(a, b-2, +2), p(a, b+2, +2)])
            if self.hasRoof:
                # base of roof
                self.basePoints.extend(line3D(
                    begin = p(a, b-1, +5),
                    end   = p(a, b+1, +5)
                ))
                self.basePoints.append(p(a, b, +6))
                # stairs for aesthetic purposes
                self.stairsPoints[0].extend([p(a, b-2, +5), p(a, b-1, +6)])
                self.stairsPoints[1].extend([p(a, b+2, +5), p(a, b+1, +6)])
                # optional pillars
                if np.random.rand() < 0.5:
                    sign = np.random.choice([-1, 1])
                    self.basePoints.extend(
                        [p(a, b + sign*2, +3), p(a, b + sign*2, +4)]
                    )
        return
        
    
    def _getB(self, a: int) -> int:
        """ Get the z coordinate of the bridge at a given x coordinate or vice versa. """
        if self.direction == 'x':
            return round(self.from_.z + (self.to_.z - self.from_.z) * (a - self.from_.x) / (self.to_.x - self.from_.x))
        else:
            return round(self.from_.x + (self.to_.x - self.from_.x) * (a - self.from_.z) / (self.to_.z - self.from_.z))
    
    @property
    def stairsDirections(self) -> tuple[str, str]:
        """ Get the directions of the stairs. """
        if self.direction == 'x':
            return ('south', 'north')
        else:
            return ('east', 'west')
    
    @property
    def direction(self) -> str:
        """ The direction of the bridge, either 'x' or 'z'. """
        if self.towers[0].district[0] == self.towers[1].district[0]:
            return 'z'
        elif self.towers[0].district[1] == self.towers[1].district[1]:
            return 'x'
        else:
            raise ValueError(
                'Invalid combination of towers: ' +
                f'{self.towers[0].district}, {self.towers[1].district}'
            )
    
    def _setTowers(self) -> None:
        """ Set the two towers in correct order. """
        if self.direction == 'x':
            self.T1, self.T2 = sorted(self.towers, key=lambda t: t.o.x)
            self.from_, self.to_ = self.T1.entrancePX, self.T2.entranceMX
        elif self.direction == 'z':
            self.T1, self.T2 = sorted(self.towers, key=lambda t: t.o.z)
            self.from_, self.to_ = self.T1.entrancePZ, self.T2.entranceMZ
        else:
            raise ValueError(f'Invalid direction: {self.direction}')
