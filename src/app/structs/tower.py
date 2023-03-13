#!/usr/bin/env python3

"""
All tower-related classes are defined here.
"""

from typing import Generator, Sequence

from gdpc import Block, Editor
from gdpc.vector_tools import Y
from glm import ivec3

from generators import fittingCylinder, cuboid3D, line3D, pyramid, cone
from materials import Air, Netherite, Beacon, GlowStone


class TowerBase:
    """
    The base of a tower.
    A tube that extends from the ground to the tower room.
    """

    def __init__(self,
            origin: ivec3,
            material: Block | Sequence[Block],
            height: int, radius: int
        ) -> None:
        """
        origin: reference point (used as center)
        height: from origin (not ground) to top of base
        radius: radius of base
        """
        self.o = origin
        self.m = material
        self.height = height
        self.radius = radius
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the tower base in Minecraft. """
        editor.placeBlock(self.wallsG, self.m)
        return
    
    @property
    def wallsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the walls. """
        r, h = self.radius, self.height
        return fittingCylinder(
            self.o + ivec3(-r, 0, -r),
            self.o + ivec3(r, h, r),
            tube = True
        )
    @property
    def wallsPC(self) -> Sequence[ivec3]:
        """ Positions of the walls. """
        return list(self.wallsG)


class TowerRoom:
    """
    The main room of a tower.
    A hollow cylinder that extends from the top of the tower base to the roof of the tower.
    """

    def __init__(self,
            origin: ivec3,
            material: Block | Sequence[Block],
            height: int, radius: int
        ) -> None:
        """
        origin: reference point (used as center)
        height: from origin (not ground) to top of room
        radius: radius of room
        """
        self.o = origin
        self.m = material
        self.height = height
        self.radius = radius
        return

    def place(self, editor: Editor) -> None:
        """ Place the tower room in Minecraft. """
        editor.placeBlock(self.wallsG, self.m)
        return

    @property
    def wallsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the walls. """
        r, h = self.radius, self.height
        return fittingCylinder(
            self.o + ivec3(-r, 0, -r),
            self.o + ivec3(r, h, r),
            hollow = True
        )
    @property
    def wallsPC(self) -> Sequence[ivec3]:
        """ Positions of the walls. """
        return list(self.wallsG)


class TowerRoof:
    """
    The roof of a tower.
    Includes the following constructs:
        * flat circular roof
        * tube from `o.y-1 < y < o.y+1` (guards)
        * hollow cone with radius "radius-4"
        * beacon on top of pyramid that shines through hollow cone
    """

    def __init__(self,
            origin: ivec3,
            baseMaterial: Block | Sequence[Block],
            coneMaterial: Block | Sequence[Block],
            beaconColor: str, height: int, radius: int
        ) -> None:
        """
        origin: reference point (used as center)
        baseMaterial: material of flat roof and guards
        coneMaterial: material of cone
        beaconColor: color of glass to be used on top of beacon
        height: from origin (not ground) to top of roof
        radius: radius of roof
        """
        self.o = origin
        self.baseM = baseMaterial
        self.coneM = coneMaterial
        self.beaconColor = beaconColor
        self.height = height
        self.radius = radius
        return

    def place(self, editor: Editor) -> None:
        """ Place all blocks of the tower roof in Minecraft. """
        editor.placeBlock(self.floorG, self.baseM)
        editor.placeBlock(self.guardsG, self.baseM)
        editor.placeBlock(self.beaconPyramidG, Netherite)
        editor.placeBlock(self.o + Y * 4, Beacon)
        editor.placeBlock(self.coneG, self.coneM)
        editor.placeBlock(self.o + Y * self.height, Air)
        stainedGlass = Block(f'{self.beaconColor}_stained_glass')
        editor.placeBlock(self.o + Y * (self.height-1), stainedGlass)
        return

    @property
    def floorG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the floor. """
        r = self.radius
        return fittingCylinder(
            self.o + ivec3(-r, 0, -r),
            self.o + ivec3(r, 0, r)
        )
    @property
    def floorPC(self) -> Sequence[ivec3]:
        """ Positions of the floor. """
        return list(self.floorG)
    
    @property
    def guardsG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the guards. """
        r = self.radius
        return fittingCylinder(
            self.o + ivec3(-r, -1, -r),
            self.o + ivec3(r, 1, r),
            tube = True
        )
    @property
    def guardsPC(self) -> Sequence[ivec3]:
        """ Positions of the guards. """
        return list(self.guardsG)
    
    @property
    def beaconPyramidG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the beacon pyramid. """
        return pyramid(
            origin = self.o + Y,
            height = 4
        )
    @property
    def beaconPyramidPC(self) -> Sequence[ivec3]:
        """ Positions of the beacon pyramid. """
        return list(self.beaconPyramidG)
    
    @property
    def coneG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the cone. """
        return cone(
            origin = self.o + Y,
            height = self.height,
            hollow = True
        )
    @property
    def conePC(self) -> Sequence[ivec3]:
        """ Positions of the cone. """
        return list(self.coneG)


class TowerRoofAccess:
    """
    A small but complex structure that allows access to the roof of a tower.
    Includes the following constructs:
        * three sets of ladders next to each other
        * horizontal plane of air at the top of the ladders
        * U shaped set of blocks to accommodate the stairs
        * stairs at the top of the ladders
        * a gate to shelter the entrance from rain
    """

    def __init__(self,
            origin: ivec3, district: str,
            baseMaterial: Block | list[Block],
            stairMaterial: Block | list[Block],
            gateMaterial: Block | list[Block],
            roomHeight: int
        ) -> None:
        """
        origin: reference point (highest central ladder)
        district: district of the tower
        baseMaterial: will be used for most blocks
        stairMaterial: material of stairs
        roomHeight: height of the tower room
        """
        self.o = origin
        self.district = district
        self.baseM = baseMaterial
        self.stairM = stairMaterial
        self.gateM = gateMaterial
        self.roomH = roomHeight
        return

    def place(self, editor: Editor) -> None:
        """ Place all blocks of the tower roof access construction in Minecraft. """
        editor.placeBlock(self.platformG, self.baseM)
        ladder = Block('ladder', {'facing': self.notFacing})
        editor.placeBlock(self.ladderG, ladder)
        self.stairM.setFacing(self.notFacing)
        for stairG in self.stairsG[:2]:
            editor.placeBlock(stairG, self.stairM)
        self.stairM.setFacing(self.facing)
        editor.placeBlock(self.stairsG[2], self.stairM)
        editor.placeBlock(self.gateG, self.gateM)
        for gapG in self.gapsG:
            editor.placeBlock(gapG, Air)
        return

    @property
    def facing(self) -> str:
        return {'w': 'west', 'e': 'east'}[self.district[1]]

    @property
    def notFacing(self) -> str:
        return {'west': 'east', 'east': 'west'}[self.facing]

    @property
    def xSign(self) -> int:
        return {'east': -1, 'west': +1}[self.facing]

    @property
    def platformG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the platform. """
        return cuboid3D(
            self.o + ivec3(self.xSign * +0, -1, -4),
            self.o + ivec3(self.xSign * +1, -1, +4)
        )
    @property
    def platformPC(self) -> Sequence[ivec3]:
        """ Positions of the platform. """
        return list(self.platformG)
    
    @property
    def ladderG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the ladder. """
        return cuboid3D(
            self.o + ivec3(0, -self.roomH+1, -1),
            self.o + ivec3(0,            -1, +1)
        )
    @property
    def ladderPC(self) -> Sequence[ivec3]:
        """ Positions of the ladder. """
        return list(self.ladderG)
    
    @property
    def stairsG(self) -> Sequence[Generator[ivec3, None, None]]:
        """ Generator for positions of the three sets of stairs. """
        return [cuboid3D(
            self.o + ivec3(self.xSign * +1, -1, -1),
            self.o + ivec3(self.xSign * +1, -1, +1)
        ), cuboid3D(
            self.o + ivec3(self.xSign * +2, 0, -1),
            self.o + ivec3(self.xSign * +2, 0, +1)
        ), cuboid3D(
            self.o + ivec3(self.xSign * -1, 0, -1),
            self.o + ivec3(self.xSign * -1, 0, +1)
        )]
    @property
    def stairsPC(self) -> Sequence[Sequence[ivec3]]:
        """ Positions of the three sets of stairs. """
        return [list(g) for g in self.stairsG]
    
    @property
    def gateG(self) -> Generator[ivec3, None, None]:
        """ Generator for positions of the gate. """
        return cuboid3D(
            self.o + ivec3(self.xSign * 0, +1, -2),
            self.o + ivec3(self.xSign * 2, +3, +2)
        )
    @property
    def gatePC(self) -> Sequence[ivec3]:
        """ Positions of the gate. """
        return list(self.gateG)
    
    @property
    def gapsG(self) -> Sequence[Generator[ivec3, None, None]]:
        """ Generator for positions of the two gaps of air. """
        return [cuboid3D(
            self.o + ivec3(self.xSign * +0, +1, -1),
            self.o + ivec3(self.xSign * +2, +2, +1)
        ), cuboid3D(
            self.o + ivec3(self.xSign * +0, 0, -1),
            self.o + ivec3(self.xSign * +1, 0, +1)
        )]
    @property
    def gapsPC(self) -> Sequence[Sequence[ivec3]]:
        """ Positions of the two gaps of air. """
        return [list(g) for g in self.gapsG]


class Tower:
    """
    A tower in one of the four districts of the city.
    """

    def __init__(self,
            district: str,
            base: TowerBase, room: TowerRoom, roof: TowerRoof,
            roofAccess: TowerRoofAccess
        ) -> None:
        """
        district: one of 'nw', 'sw', 'se', 'ne'
        base: TowerBase instance
        room: TowerRoom instance
        roof: TowerRoof instance
        roofAccess: TowerRoofAccess instance

        ! Note: tower.o(rigin) is set to room.o(rigin) !
        """
        assert district in ['nw', 'sw', 'se', 'ne'], f'Invalid district: {district}'
        self.district = district

        self.base = base
        self.room = room
        self.roof = roof
        self.roofAccess = roofAccess
        self.o = self.room.o
        return

    def place(self, editor: Editor) -> None:
        """ Place the tower in Minecraft. """
        self.base.place(editor)
        self.room.place(editor)
        self.roof.place(editor)
        self.roofAccess.place(editor)
        for entranceG in self.entrancesG:
            editor.placeBlock(entranceG, Air)
        return

    @property
    def entranceOrigins(self) -> dict[str, ivec3]:
        """ Each tower has a unique set of 2 entrances, depending on its district. """
        return {
            'x': self.o + ivec3(self.xSign * self.room.radius, 0, 0),
            'z':  self.o + ivec3(0, 0, self.zSign * self.room.radius)
        }

    @property
    def entranceDirections(self) -> list[str]:
        """ Each tower has a unique set of 2 entrance directions, depending on its district. """
        return {
            'nw': ['south', 'east'],
            'sw': ['north', 'east'],
            'se': ['north', 'west'],
            'ne': ['south', 'west']
        }[self.district]
    
    @property
    def zSign(self) -> int:
        return {'north': -1, 'south': +1}[self.entranceDirections[0]]

    @property
    def xSign(self) -> int:
        return {'west': -1, 'east': +1}[self.entranceDirections[1]]

    @property
    def entrancesG(self) -> Sequence[Generator[ivec3, None, None]]:
        """ Generator for positions of the two entrances. """
        x, z = self.xSign, self.zSign
        r = self.room.radius
        return [cuboid3D(
            self.o + ivec3(x*r, 1, -1),
            self.o + ivec3(x*r, 3, +1)
        ), cuboid3D(
            self.o + ivec3(-1, 1, z*r),
            self.o + ivec3(+1, 3, z*r)
        )]
    @property
    def entrancesPC(self) -> Sequence[Sequence[ivec3]]:
        """ Positions of the two entrances. """
        return [list(g) for g in self.entrancesG]
