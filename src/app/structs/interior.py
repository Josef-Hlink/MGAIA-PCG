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
from materials import BaseSlabPalette, pot, signBlock, Air, Chain, Lantern, SoulLantern, GrassBlock


class Interior:
    """ base class """

    def __init__(self, tower: Tower) -> None:
        self.o = tower.o
        self.district = tower.district
        self.radius = tower.room.radius - 1
        self.height = tower.room.height - 1
        return

    @property
    def floorG(self) -> Generator[ivec3, None, None]:
        """ Generator for the floor. """
        return fittingCylinder(
            self.o + ivec3(-self.radius, 0, -self.radius),
            self.o + ivec3(+self.radius, 0, +self.radius)
        )

    @property
    def plinthG(self) -> Generator[ivec3, None, None]:
        """ Generator for the plinth. """
        return fittingCylinder(
            self.o + ivec3(-self.radius, 0, -self.radius),
            self.o + ivec3(+self.radius, 0, +self.radius),
            tube = True
        )

    @property
    def ceilingG(self) -> Generator[ivec3, None, None]:
        """ Generator for the ceiling. """
        yield from [p for p in fittingCylinder(
            self.o + ivec3(-self.radius, self.height, -self.radius),
            self.o + ivec3(+self.radius, self.height, +self.radius)
            ) if p.x != self.o.x + self.xSign * self.radius
        ]

    def _fixLanternChains(self, n: int) -> None:
        """ Static point collection for the lantern chains. """
        r, h = self.radius - 3, self.height
        candidates = list(fittingCylinder(self.o + ivec3(-r, h, -r), self.o + ivec3(+r, h, +r)))
        candidates = list(filter(lambda c: c not in self.invalidLanternPC, candidates))
        self.lanternChainsPC = []
        for o in [candidates[i] for i in np.random.choice(len(candidates), n, replace = False)]:
            self.lanternChainsPC.append([o - Y * i for i in range(np.random.randint(1, 4))])
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
    
    def _getTextSign(self, facing: str, woodType: str) -> Block:
        """ Get the text sign for the given direction. """
        return signBlock(
            wood = woodType, wall = True,
            facing = {'n': 'north', 'e': 'east', 's': 'south', 'w': 'west'}[facing],
            line1 = 'When', line2 = 'You\'re Lost',
            line3 = 'in the', line4 = 'Darkness',
            color = 'black', isGlowing = True
        )

    @property
    def xSign(self) -> int:
        """ Sign of the x coordinate. """
        return {'w': -1, 'e': 1}[self.district[1]]
    
    @property
    def zSign(self) -> int:
        """ Sign of the z coordinate. """
        return {'n': -1, 's': 1}[self.district[0]]


class NostalgicInterior(Interior):
    """ Nostalgic interior with a small birch house and a birch tree on a grass plane. """

    def __init__(self, tower: Tower) -> None:
        super().__init__(tower)
        self.direction = self.district[0]
        self.garden = NostalgicGarden(self.o, self.height, self.district[0])
        self._fixLanternChains(3)
        return

    def place(self, editor: Editor) -> None:
        """ Place the interior in Minecraft. """
        editor.placeBlock(self.floorG, Block('birch_slab', {'type': 'bottom'}))
        editor.placeBlock(self.plinthG, Block('birch_planks'))
        editor.placeBlock(self.ceilingG, BaseSlabPalette('top'))
        editor.placeBlock(self.lanternChainsG, Chain)
        editor.placeBlock(self.lanternsG, Lantern)
        xS, zS, r = self.xSign, self.zSign, self.radius
        xE, zE = self.o + ivec3(xS * -r, 4, 0), self.o + ivec3(0, 4, zS * -r)
        editor.placeBlock(xE, self._getTextSign(self.district[1], 'birch'))
        editor.placeBlock(zE, self._getTextSign(self.district[0], 'birch'))
        self.garden.place(editor)

        editor.placeBlock(self.houseOutlineG, Block('birch_planks'))
        editor.placeBlock(self.houseBackWallG, Block('birch_planks'))
        editor.placeBlock(self.houseDoorG, Air)
        editor.placeBlock(
            self.o + ivec3(-2, 1, self.zSign * 3),
            Block('birch_door', {'hinge': 'left', 'half': 'lower', 'facing': self.facing}))
        editor.placeBlock(self.o + ivec3(-2, 3, self.zSign * 2), self.houseTextSign)
        editor.placeBlock(self.o + ivec3(-1, 2, self.zSign * 2), Block('wall_torch', {'facing': {'n': 'south', 's': 'north'}[self.direction]}))

        editor.placeBlock(self.o + ivec3(2, 1, self.zSign * 8), Block('white_bed', {'part': 'foot', 'facing': self.facing}))
        editor.placeBlock(self.o + ivec3(2, 2, self.zSign * 9), self.bedTextSign)
        editor.placeBlock(self.o + ivec3(0, 2, self.zSign * 10), pot('orange_tulip'))
        lr1, lr2 = ('left', 'right') if self.direction == 's' else ('right', 'left')
        editor.placeBlock(self.o + ivec3(-2, 1, self.zSign * 8), Block('chest', {'facing': 'east', 'type': lr1}))
        editor.placeBlock(self.o + ivec3(-2, 1, self.zSign * 9), Block('chest', {'facing': 'east', 'type': lr2}))
        editor.placeBlock(
            self.o + ivec3(1, 1, self.zSign * 9),
            Block('chest',
                {'facing': {'n': 'south', 's': 'north'}[self.direction]},
                data = f'{{Items:[{{Slot:13b,id:"minecraft:iron_sword",Count:1b}}]}}'
            ))
        editor.placeBlock(self.o + ivec3(2, 1, self.zSign * 4), Block('crafting_table'))
        editor.placeBlock(self.o + ivec3(2, 1, self.zSign * 6), Block('furnace', {'facing': 'west', 'lit': 'true'}))
        editor.placeBlock(self.o + ivec3(0, 1, self.zSign * 4), Block('bookshelf'))
        editor.placeBlock(self.o + ivec3(-2, 3, self.zSign * 4), Block('wall_torch', {'facing': self.facing}))
        return

    @property
    def facing(self) -> str:
        """ The facing direction. """
        return {'n': 'north', 's': 'south'}[self.direction]

    @property
    def houseOutlineG(self) -> Generator[ivec3, None, None]:
        """ Generator for the house outline. """
        full = cuboid3D(
            self.o + ivec3(-3, 1, self.zSign * 3),
            self.o + ivec3(3, 5, self.zSign * 9)
        )
        inside = set(cuboid3D(
            self.o + ivec3(-2, 1, self.zSign * 4),
            self.o + ivec3(2, 4, self.zSign * 9)
        ))
        yield from [b for b in full if b not in inside]
        return

    @property
    def houseBackWallG(self) -> Generator[ivec3, None, None]:
        """ Generator for the house back wall with a cross shape cutout. """
        full = cuboid3D(
            self.o + ivec3(-2, 1, self.zSign * 10),
            self.o + ivec3(2, 5, self.zSign * 10)
        )
        cutout = list(line3D(
            self.o + ivec3(0, 2, self.zSign * 10),
            self.o + ivec3(0, 5, self.zSign * 10)
        )) + list(line3D(
            self.o + ivec3(-1, 4, self.zSign * 10),
            self.o + ivec3(1, 4, self.zSign * 10)
        ))
        yield from [b for b in full if b not in cutout]
        return

    @property
    def houseDoorG(self) -> Generator[ivec3, None, None]:
        """ Generator for the house door. """
        return line3D(
            self.o + ivec3(-2, 1, self.zSign * 3),
            self.o + ivec3(-2, 2, self.zSign * 3)
        )

    @property
    def houseTextSign(self) -> Block:
        """ The text sign for the house. """
        return signBlock(
            wood = 'birch', wall = True, facing = {'n': 'south', 's': 'north'}[self.direction],
            line1 = 'live', line2 = 'laugh', line3 = 'love', line4 = 'craft',
            color = 'black'
        )

    @property
    def bedTextSign(self) -> Block:
        """ The text sign for the bed. """
        return signBlock(
            wood = 'birch', wall = True, facing = 'west',
            line1 = 'Don\'t', line2 = 'Forget', line3 = 'to', line4 = 'Sleep',
            color = 'black'
        )

    @property
    def invalidLanternPC(self) -> Sequence[ivec3]:
        """ Invalid lantern point collection. """
        return [ivec3(p.x, self.o.y + self.height, p.z) for p in [*self.houseOutlineG, *self.garden.treeLeavesG]]


class EndGameInterior(Interior):
    """ Interior with an endgame feel. """

    def __init__(self, tower: Tower) -> None:
        super().__init__(tower)
        self.district = tower.district
        self.table = Table(tower.o, 'deepslate', 'wither_rose')
        self.endPortal = EndPortal(self.o + ivec3(0, 0, self.zSign * 7))
        self._fixLanternChains(20)

    def place(self, editor: Editor) -> None:
        """ Place the interior in Minecraft. """
        editor.placeBlock(self.floorG, Block('deepslate_tile_slab', {'type': 'bottom'}))
        editor.placeBlock(self.plinthG, Block('deepslate_tiles'))
        editor.placeBlock(self.ceilingG, BaseSlabPalette('top'))
        lichenStates = {d: 'true' for d in ['north', 'east', 'south', 'west', 'up', 'down']}
        editor.placeBlock(self.lichenG, Block('glow_lichen', lichenStates))
        self.table.place(editor)
        editor.placeBlock(self.lanternChainsG, Chain)
        editor.placeBlock(self.lanternsG, SoulLantern)
        xS, zS, r = self.xSign, self.zSign, self.radius
        xE, zE = self.o + ivec3(xS * -r, 4, 0), self.o + ivec3(0, 4, zS * -r)
        editor.placeBlock(xE, self._getTextSign(self.district[1], 'spruce'))
        editor.placeBlock(zE, self._getTextSign(self.district[0], 'spruce'))
        self.endPortal.place(editor)
        editor.placeBlock(self.o + ivec3(0, 2, self.zSign * 7), Block('deepslate_tiles'))
        editor.placeBlock(
            self.o + ivec3(0, 3, self.zSign * 7),
            Block('ender_chest', {'facing': {'n': 'south', 's': 'north'}[self.district[0]]})
        )

    @property
    def invalidLanternPC(self) -> Sequence[ivec3]:
        """ Invalid lantern point collection. """
        return []

    @property
    def ceilingG(self) -> Generator[ivec3, None, None]:
        return fittingCylinder(
            self.o + ivec3(-(self.radius-1), self.height, -(self.radius-1)),
            self.o + ivec3((self.radius-1), self.height, (self.radius-1))
        )

    @property
    def lichenG(self) -> Generator[ivec3, None, None]:
        """ Generator for the glow lichen. """
        yield from [p for p in fittingCylinder(
                self.o + ivec3(-self.radius, 1, -self.radius),
                self.o + ivec3(self.radius, self.height, self.radius),
                tube = True
            ) if p.x != self.o.x + self.xSign * self.radius
        ]


class ExoticWoodInterior(Interior):
    """ Exotic (crimson or warped) wood interior. """

    def __init__(self, tower: Tower, kind: str) -> None:
        assert kind in ['crimson', 'warped'], f'Invalid wood type: {kind}, must be crimson or warped.'
        super().__init__(tower)
        self.kind = kind
        self.gardens = {district: None for district in ['nw', 'ne', 'sw', 'se']}
        for district in self.gardens.keys():
            xs, zs = {'w': -1, 'e': 1}[district[1]], {'n': -1, 's': 1}[district[0]]
            gO = self.o + ivec3(xs * 3, 0, zs * 3)
            garden = ExoticGarden(gO, self.kind, self.height, district)
            self.gardens[district] = garden
        self.table = Table(self.o, self.kind, self.kind + '_fungus')
        if self.kind == 'crimson':
            self._fixLanternChains(5)
            self.lantern = Lantern
        else:
            self._fixLanternChains(10)
            self.lantern = SoulLantern
        return

    def place(self, editor: Editor) -> None:
        """ Place the interior in Minecraft. """
        editor.placeBlock(self.floorG, Block(f'{self.kind}_slab', {'type': 'bottom'}))
        editor.placeBlock(self.plinthG, Block(f'{self.kind}_planks'))
        editor.placeBlock(self.ceilingG, BaseSlabPalette('top'))
        editor.placeBlock(self.lanternChainsG, Chain)
        editor.placeBlock(self.lanternsG, self.lantern)
        for garden in self.gardens.values():
            garden.place(editor)
        self.table.place(editor)
        xS, zS, r = self.xSign, self.zSign, self.radius
        xE, zE = self.o + ivec3(xS * -r, 4, 0), self.o + ivec3(0, 4, zS * -r)
        editor.placeBlock(xE, self._getTextSign(self.district[1], self.kind))
        editor.placeBlock(zE, self._getTextSign(self.district[0], self.kind))
        return
        
    @property
    def invalidLanternPC(self) -> Sequence[ivec3]:
        """ Invalid lantern point collection. """
        invalid = []
        for garden in self.gardens.values():
            invalid.extend(garden.hyphaeG)
            invalid.extend(garden.boundsG)
        return invalid


class NostalgicGarden:
    """ A grass garden spanning the x axis. """

    def __init__(self, origin: ivec3, height: int, direction: str) -> None:
        """
        origin: the origin of the garden (same as room origin).
        height: room height.
        direction: the direction the garden points to (n or s).
        """
        self.o = origin
        self.height = height
        self.direction = direction
        return

    def place(self, editor: Editor) -> None:
        """ Place the garden in Minecraft. """
        editor.placeBlock(self.grassBlocksG, GrassBlock)
        editor.placeBlock(self.boundsG, Block('birch_planks'))
        editor.placeBlock(self.floorGapG, Air)
        editor.placeBlock(self.canalG, Block('water'))
        editor.placeBlock(self.treeLeavesG, Block('birch_leaves'))
        editor.placeBlock(self.treeTrunkG, Block('birch_log'))
        return
    
    @property
    def sign(self) -> int:
        """ The sign of the z coordinate. """
        return {'n': -1, 's': 1}[self.direction]
    
    @property
    def facing(self) -> str:
        """ The facing direction. """
        return {'n': 'north', 's': 'south'}[self.direction]

    @property
    def treeTrunkG(self) -> Generator[ivec3, None, None]:
        """ Generator for the tree trunk. """
        return line3D(
            self.o + ivec3(-4, 0, self.sign * -5),
            self.o + ivec3(-4, 5, self.sign * -5)
        )

    @property
    def treeLeavesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the tree leaves. """
        yield from fittingCylinder(
            self.o + ivec3(-1, 3, self.sign * -2),
            self.o + ivec3(-7, 5, self.sign * -8)
        )
        yield from fittingCylinder(
            self.o + ivec3(-2, 6, self.sign * -3),
            self.o + ivec3(-6, 6, self.sign * -7)
        )
        yield from cuboid3D(
            self.o + ivec3(-3, 7, self.sign * -4),
            self.o + ivec3(-5, 7, self.sign * -6)
        )
        return

    @property
    def floorGapG(self) -> Generator[ivec3, None, None]:
        """ Generator for the floor gap. """
        return cuboid3D(
            self.o + ivec3(-3, 0, self.sign * -4),
            self.o + ivec3(-5, 0, self.sign * -6)
        )
    
    @property
    def canalG(self) -> Generator[ivec3, None, None]:
        """ Generator for the canal. """
        pc = []
        pc.extend(line3D(
            self.o + ivec3(-4, 0, self.sign * 2),
            self.o + ivec3(-4, 0, self.sign * 8)
        ))
        pc.extend(line3D(
            self.o + ivec3(4, 0, self.sign * 2),
            self.o + ivec3(4, 0, self.sign * 8)
        ))
        pc.extend(line3D(
            self.o + ivec3(-4, 0, self.sign * 2),
            self.o + ivec3(4, 0, self.sign * 2)
        ))
        pc.remove(self.o + ivec3(-2, 0, self.sign * 2))
        yield from pc

    @property
    def grassBlocksG(self) -> Generator[ivec3, None, None]:
        """ Generator for the grass blocks. """
        yield from triangle(self.o + ivec3(4, 0, self.sign * 4), 5, self.direction + 'e')
        yield from triangle(self.o + ivec3(-4, 0, self.sign * 4), 5, self.direction + 'w')
        yield from triangle(self.o + ivec3(4, 0, self.sign * 3), 5, self.opp(self.direction) + 'e')
        yield from triangle(self.o + ivec3(-4, 0, self.sign * 3), 5, self.opp(self.direction) + 'w')
        yield from cuboid3D(
            self.o + ivec3(-3, 0, self.sign * 4),
            self.o + ivec3(3, 0, self.sign * 9)
        )
        yield from cuboid3D(
            self.o + ivec3(-3, 0, self.sign * 3),
            self.o + ivec3(3, 0, self.sign * -1)
        )
        yield from cuboid3D(
            self.o + ivec3(-3, -1, self.sign * -4),
            self.o + ivec3(-5, -1, self.sign * -6)
        )
        yield from cuboid3D(
            self.o + ivec3(-4, -1, self.sign * 2),
            self.o + ivec3(4, -1, self.sign * 8)
        )
        return

    @property
    def boundsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the bounds of the garden. """
        yield from line3D(
            self.o + ivec3(-4, 0, self.sign * -2),
            self.o + ivec3(4, 0, self.sign * -2)
        )
        yield from line3D(
            self.o + ivec3(-4, 0, self.sign * -2),
            self.o + ivec3(-9, 0, self.sign * +3)
        )
        yield from line3D(
            self.o + ivec3(4, 0, self.sign * -2),
            self.o + ivec3(9, 0, self.sign * +3)
        )
        return

    def opp(self, direction: str) -> str:
        """ Opposite direction. """
        return {'n': 's', 's': 'n'}[direction]


class ExoticGarden:
    """ A garden (crimson or warped) to be placed in one of the corners of a tower. """

    def __init__(self, origin: ivec3, kind: str, height: int, district: str):
        """
        origin: the origin of the garden (the closest corner to the tower room's origin).
        kind: the kind of garden (nylium or warped).
        height: room height.
        district: the district the garden points to (nw, ne, sw, se).
        """
        self.o = origin
        self.kind = kind
        self.height = height
        self.district = district
        self.vinesName = 'weeping' if kind == 'crimson' else 'twisting'
        return

    def place(self, editor: Editor):
        """ Place the structure. """
        editor.placeBlock(self.nyliumG, Block(f'{self.kind}_nylium'))
        editor.placeBlock(self.hyphaeG, Block(f'{self.kind}_hyphae'))
        editor.placeBlock(self.boundsG, Block(f'{self.kind}_planks'))
        editor.placeBlock(self.fencesG, Block(f'{self.kind}_fence'))
        editor.placeBlock(self.rootsG, Block(f'{self.kind}_roots'))
        editor.placeBlock(self.vinesG, Block(f'{self.vinesName}_vines'))
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
    def boundsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the garden bounds. """
        o, h = self.o, self.height
        xs, zs = self.xSign, self.zSign
        for y in [0, self.height]:
            yield from line3D(o + ivec3(0, y, 0), o + ivec3(xs * 6, y, 0))
            yield from line3D(o + ivec3(0, y, 0), o + ivec3(0, y, zs * 6))
        for x, z in [(0, 6), (6, 0)]:
            yield from line3D(o + ivec3(xs * x, 1, zs * z), o + ivec3(xs * x, h-1, zs * z))
    
    @property
    def fencesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the garden fences. """
        o, h = self.o, self.height
        xs, zs = self.xSign, self.zSign
        for x in range(0, 5, 2):
            yield from line3D(o + ivec3(xs * x, 1, 0), o + ivec3(xs * x, h-1, 0))
        for z in range(0, 5, 2):
            yield from line3D(o + ivec3(0, 1, zs * z), o + ivec3(0, h-1, zs * z))

    @property
    def vinesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the vines. """
        return self.weepingVinesG if self.kind == 'crimson' else self.twistingVinesG

    @property
    def weepingVinesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the weeping vines. """
        candidates = list(self.hyphaeG)
        origins = [candidates[i] for i in np.random.choice(len(candidates), 5, replace=False)]
        for o in origins:
            yield from [o - Y * i for i in range(0, np.random.randint(3, 7))]
        return

    @property
    def twistingVinesG(self) -> Generator[ivec3, None, None]:
        """ Generator for the twisting vines. """
        candidates = list(self.nyliumG)
        candidates = list(filter(lambda p: p not in self.rootsG, candidates))
        origins = [candidates[i] for i in np.random.choice(len(candidates), 5, replace=False)]
        for o in origins:
            yield from [o + Y * i for i in range(1, np.random.randint(4, 8))]
        return

    @property
    def rootsG(self) -> Generator[ivec3, None, None]:
        """ Generator for the roots. """
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


class Table:
    """ A table to be placed in the middle of a tower room. """

    def __init__(self, origin: ivec3, material: str, plant: str) -> None:
        self.o = origin
        self.m = material
        self.baseM = Block(material + '_planks') if material in ['crimson', 'warped'] else Block(material + '_tiles')
        self.legM = Block(material + '_fence') if material in ['crimson', 'warped'] else Block(material + '_tile_wall')
        self.slabM = Block(material + '_slab') if material in ['crimson', 'warped'] else Block(material + '_tile_slab')
        self.plant = plant
        return

    def place(self, editor: Editor) -> None:
        """ Place the table in Minecraft. """
        editor.placeBlock(self.baseG, self.baseM)
        editor.placeBlock(self.cutoutG, Air)
        editor.placeBlock(self.legsG, self.legM)
        editor.placeBlock(self.topG, self.slabM)
        editor.placeBlock(self.o + Y*2, pot(self.plant))
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


class EndPortal:
    """ A working end portal with a deepslate tile wall around it. """

    def __init__(self, origin: ivec3) -> None:
        self.o = origin
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the end portal in Minecraft. """
        editor.placeBlock(
            cuboid3D(self.o + ivec3(-1, -1, -1), self.o + ivec3(1, -1, 1)),
            Block('deepslate_tiles')
        )
        editor.placeBlock(
            cuboid3D(self.o + ivec3(-1, 0, -1), self.o + ivec3(1, 0, 1)),
            Block('end_portal')
        )
        for x1, x2, z1, z2, facing in (
            (-2, 2, -2, -2, 'south'),
            (-2, 2, 2, 2, 'north'),
            (-2, -2, -2, 2, 'east'),
            (2, 2, -2, 2, 'west')
        ):
            editor.placeBlock(
                line3D(self.o + ivec3(x1, 0, z1), self.o + ivec3(x2, 0, z2)),
                Block('end_portal_frame', {'facing': facing, 'eye': 'true'})
            )
            editor.placeBlock(
                line3D(self.o + ivec3(x1, 1, z1), self.o + ivec3(x2, 1, z2)),
                Block('deepslate_tile_wall')
            )
        for x, z in ((-2, -2), (-2, 2), (2, -2), (2, 2)):
            editor.placeBlock(self.o + ivec3(x, 0, z), Block('deepslate_tiles'))
        editor.placeBlock(
            cuboid3D(self.o + ivec3(-2, 2, -2), self.o + ivec3(2, 2, 2)),
            Block('deepslate_tile_slab', {'type': 'bottom'})
        )
        return
