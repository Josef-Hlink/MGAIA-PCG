#!/usr/bin/env python3

"""
Four different interiors for the tower rooms.
"""

from typing import Generator, Sequence

import numpy as np

from gdpc import Block, Editor
from gdpc.vector_tools import Y
from glm import ivec3

from .tower import Tower
from generators import cuboid3D, fittingCylinder, line3D, triangle
from materials import (Air, BaseSlabPalette, CrimsonPlanks, CrimsonSlab, CrimsonFence, CrimsonSign, CrimsonRoots, WeepingVines,
                       Lantern, SoulLantern, Chain, GlowStone, Pot, CrimsonNylium, CrimsonHyphae, signBlock)

class Interior:
    """ base class """

    def __init__(self, tower: Tower) -> None:
        self.o = tower.o
        self.district = tower.district
        self.radius = tower.room.radius - 1
        self.height = tower.room.height - 1
        return

    @property
    def floorGenerator(self) -> Generator[ivec3, None, None]:
        """ Generator for the floor. """
        return fittingCylinder(
            self.o + ivec3(-self.radius, 0, -self.radius),
            self.o + ivec3(+self.radius, 0, +self.radius)
        )

    @property
    def plinthGenerator(self) -> Generator[ivec3, None, None]:
        """ Generator for the plinth. """
        return fittingCylinder(
            self.o + ivec3(-self.radius, 0, -self.radius),
            self.o + ivec3(+self.radius, 0, +self.radius),
            tube = True
        )

    @property
    def ceilingG(self) -> Generator[ivec3, None, None]:
        """ Generator for the ceiling. """
        # filter out the points that would interfere with the ladders (at the x extremes)
        yield from [p for p in fittingCylinder(
            self.o + ivec3(-self.radius, self.height, -self.radius),
            self.o + ivec3(+self.radius, self.height, +self.radius)
            ) if p.x != self.o.x + self.xSign * self.radius
        ]

    def _fixLanternChains(self, n: int) -> None:
        """ Static point collection for the lantern chains. """
        r, h = self.radius - 3, self.height
        candidates = list(fittingCylinder(self.o + ivec3(-r, h, -r), self.o + ivec3(+r, h, +r)))
        # filter out invalid candidates
        candidates = list(filter(lambda c: c not in self.invalidLanternPC, candidates))
        self.lanternChainsPC = []
        for o in [candidates[i] for i in np.random.choice(len(candidates), n, replace = False)]:
            self.lanternChainsPC.append([o - Y * i for i in range(np.random.randint(1, 3))])
        return
    
    @property
    def lanternChainsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the lantern chains. """
        for pc in self.lanternChainsPC:
            yield from pc
            
    @property
    def lanternsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the lanterns. """
        for pc in self.lanternChainsPC:
            yield pc[-1] - Y
    
    @property
    def xSign(self) -> int:
        """ Sign of the x coordinate. """
        return {'w': -1, 'e': 1}[self.district[1]]
    
    @property
    def zSign(self) -> int:
        """ Sign of the z coordinate. """
        return {'n': -1, 's': 1}[self.district[0]]

    @property
    def otherDistricts(self) -> str:
        """ The other districts. """
        return [d for d in ['nw', 'ne', 'sw', 'se'] if d != self.district]


class CrimsonInterior(Interior):
    """ Crimson interior. """

    def __init__(self, tower: Tower) -> None:
        super().__init__(tower)
        self.gardens = {district: None for district in ['nw', 'ne', 'sw', 'se']}
        for district in self.gardens.keys():
            xs, zs = {'w': -1, 'e': 1}[district[1]], {'n': -1, 's': 1}[district[0]]
            gO = self.o + ivec3(xs * 3, 0, zs * 3)
            garden = NyliumGarden(gO, self.height, district)
            self.gardens[district] = garden
        self.table = Table(self.o, 'crimson', 'crimson_fungus')
        self._fixLanternChains(5)
        return


    def place(self, editor: Editor) -> None:
        """ Place the interior in Minecraft. """
        editor.placeBlock(self.floorGenerator, CrimsonSlab)
        editor.placeBlock(self.plinthGenerator, CrimsonPlanks)
        editor.placeBlock(self.ceilingG, BaseSlabPalette('top'))
        editor.placeBlock(self.lanternChainsG, Chain)
        editor.placeBlock(self.lanternsG, Lantern)
        xEntrance = self.o + ivec3(self.xSign * -self.radius, 4, 0)
        zEntrance = self.o + ivec3(0, 4, self.zSign * -self.radius)
        editor.placeBlock(xEntrance, self._getTextSign(self.district[1]))
        editor.placeBlock(zEntrance, self._getTextSign(self.district[0]))
        for garden in self.gardens.values():
            garden.place(editor)
        self.table.place(editor)
        return

    @property
    def invalidLanternPC(self) -> Sequence[ivec3]:
        """ Invalid lantern point collection. """
        invalid = []
        for garden in self.gardens.values():
            invalid.extend(garden.hyphaeG)
            invalid.extend(garden.gardenBoundsG)
        return invalid

    def _getTextSign(self, facing: str) -> Block:
        """ Get the text sign for the given direction. """
        return signBlock(
            wood = 'crimson', wall = True,
            facing = {'n': 'north', 'e': 'east', 's': 'south', 'w': 'west'}[facing],
            line1 = 'When', line2 = 'You\'re Lost',
            line3 = 'in the', line4 = 'Darkness',
            color = 'black', isGlowing = True
        )

class Table:
    """ A table to be placed in the middle of a tower room. """

    def __init__(self, origin: ivec3, woodType: str, plant: str) -> None:
        self.o = origin
        self.woodType = woodType
        self.plant = plant
        return

    def place(self, editor: Editor) -> None:
        """ Place the table in Minecraft. """
        editor.placeBlock(self.baseG, Block(self.woodType + '_planks'))
        editor.placeBlock(self.cutoutG, Air)
        editor.placeBlock(self.legsG, Block(self.woodType + '_fence'))
        editor.placeBlock(self.topG, Block(self.woodType + '_slab'))
        editor.placeBlock(self.o + Y*2, Pot(self.plant))
        return

    @property
    def baseG(self) -> Generator[ivec3, None, None]:
        """ Generator for the table base. """
        return cuboid3D(
            self.o + ivec3(-1, -1, -1),
            self.o + ivec3(+1, -1, +1)
        )

    @property
    def cutoutG(self) -> Generator[ivec3, None, None]:
        """ Generator for the table cutout. """
        return cuboid3D(
            self.o + ivec3(-1, 0, -1),
            self.o + ivec3(+1, 0, +1)
        )

    @property
    def legsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the table legs. """
        for x, z in [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]:
            yield self.o + ivec3(x, 0, z)

    @property
    def topG(self) -> Generator[ivec3, None, None]:
        """ Generator for the tabletop. """
        return cuboid3D(
            self.o + ivec3(-1, 1, -1),
            self.o + ivec3(+1, 1, +1)
        )


class NyliumGarden:
    """ A nylium garden to be placed in one of the corners of the crimson tower. """

    def __init__(self, origin: ivec3, height: int, district: str):
        """
        origin: the origin of the garden (the closest corner to the tower room's origin).
        height: room height
        district: the district of the garden (nw, ne, sw, se)
        """
        self.o = origin
        self.height = height
        self.district = district
        return

    def place(self, editor: Editor):
        """ Place the structure. """
        editor.placeBlock(self.nyliumG, CrimsonNylium)
        editor.placeBlock(self.hyphaeG, CrimsonHyphae)
        editor.placeBlock(self.gardenBoundsG, CrimsonPlanks)
        editor.placeBlock(self.gardenFencesG, CrimsonFence)
        editor.placeBlock(self.crimsonRootsG, CrimsonRoots)
        editor.placeBlock(self.weepingVinesG, WeepingVines)
        return    

    @property
    def nyliumG(self) -> Generator[ivec3, None, None]:
        """ Generator for the nylium blocks. """
        return triangle(self.o + ivec3(self.xSign, 0, self.zSign), 6, self.district)
    
    @property
    def hyphaeG(self) -> Generator[ivec3, None, None]:
        """ Generator for the hyphae blocks. """
        yield from [p + Y * self.height for p in self.nyliumG]
    
    @property
    def gardenBoundsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the garden bounds. """
        o, h = self.o, self.height
        xs, zs = self.xSign, self.zSign
        for y in [0, self.height]:
            yield from line3D(o + ivec3(0, y, 0), o + ivec3(xs * 6, y, 0))
            yield from line3D(o + ivec3(0, y, 0), o + ivec3(0, y, zs * 6))
        for x, z in [(0, 6), (6, 0)]:
            yield from line3D(o + ivec3(xs * x, 1, zs * z), o + ivec3(xs * x, h-1, zs * z))
    
    @property
    def gardenFencesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the garden fences. """
        o, h = self.o, self.height
        xs, zs = self.xSign, self.zSign
        for x in range(0, 5, 2):
            yield from line3D(o + ivec3(xs * x, 1, 0), o + ivec3(xs * x, h-1, 0))
        for z in range(0, 5, 2):
            yield from line3D(o + ivec3(0, 1, zs * z), o + ivec3(0, h-1, zs * z))

    @property
    def weepingVinesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the weeping vines. """
        candidates = list(self.hyphaeG)
        origins = [candidates[i] for i in np.random.choice(len(candidates), 5, replace=False)]
        for o in origins:
            yield from [o - Y * i for i in range(1, np.random.randint(3, 7))]
        return

    @property
    def crimsonRootsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the crimson roots. """
        candidates = list(self.nyliumG)
        yield from [candidates[i] + Y for i in np.random.choice(len(candidates), 5, replace=False)]
        return
    
    @property
    def xSign(self) -> int:
        """ Sign of the x coordinate. """
        return {'w': -1, 'e': 1}[self.district[1]]
    
    @property
    def zSign(self) -> int:
        """ Sign of the z coordinate. """
        return {'n': -1, 's': 1}[self.district[0]]
