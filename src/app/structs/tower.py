#!/usr/bin/env python3

"""
All tower-related classes are defined here.
"""

from gdpc import Block, Editor
from gdpc.vector_tools import Y
from glm import ivec3

from generators import fittingCylinder, cuboid3D, line3D, pyramid, cone
from materials import Air, Netherite, Beacon


class TowerBase:
    """
    The base of a tower.
    A tube that extends from the ground to the tower room.
    """

    def __init__(self,
            origin: ivec3,
            material: Block | list[Block],
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
        self._setGenerators()
        return

    def _setGenerators(self) -> None:
        """ Determine the locations of all blocks of the tower base. """
        r, h = self.radius, self.height
        self.baseGenerator = fittingCylinder(
            self.o + ivec3(-r, 0, -r),
            self.o + ivec3(r, h, r),
            tube = True
        )
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the tower base in Minecraft. """
        editor.placeBlock(self.baseGenerator, self.m)
        return


class TowerRoom:
    """
    The main room of a tower.
    A hollow cylinder that extends from the top of the tower base to the roof of the tower.
    """

    def __init__(self,
            origin: ivec3,
            material: Block | list[Block],
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
        self._setGenerators()
        return

    def _setGenerators(self) -> None:
        """ Determine the locations of all blocks of the tower room. """
        r, h = self.radius, self.height
        self.baseGenerator = fittingCylinder(
            self.o + ivec3(-r, 0, -r),
            self.o + ivec3(r, h, r),
            hollow = True
        )
        return
    
    def place(self, editor: Editor) -> None:
        """ Place the tower room in Minecraft. """
        editor.placeBlock(self.baseGenerator, self.m)
        return


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
            baseMaterial: Block | list[Block],
            coneMaterial: Block | list[Block],
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
        self._setGenerators()
        return

    def _setGenerators(self) -> None:
        """ Determine the locations of (almost) all blocks of the tower roof. """
        r = self.radius
        self.baseGenerator = fittingCylinder(
            corner1 = self.o + ivec3(-r, 0, -r),
            corner2 = self.o + ivec3(r, 0, r)
        )
        self.guardsGenerator = fittingCylinder(
            corner1 = self.o + ivec3(-r, -1, -r),
            corner2 = self.o + ivec3(r, 1, r),
            tube = True
        )
        self.pyramidGenerator = pyramid(
            origin = self.o + Y,
            height = 4
        )
        self.coneGenerator = cone(
            origin = self.o + Y,
            height = self.height,
            hollow = True
        )
        return
    
    def place(self, editor) -> None:
        """ Place all blocks of the tower roof in Minecraft. """
        # base and guards
        editor.placeBlock(self.baseGenerator, self.baseM)
        editor.placeBlock(self.guardsGenerator, self.baseM)
        
        # pyramid and beacon
        editor.placeBlock(self.pyramidGenerator, Netherite)
        editor.placeBlock(
            self.o + Y * 4,
            Beacon
        )

        # top cone and beacon glass
        editor.placeBlock(self.coneGenerator, self.coneM)
        editor.placeBlock(self.o + Y * self.height, Air)
        editor.placeBlock(
            self.o + Y * (self.height-1),
            Block(f'{self.beaconColor}_stained_glass')
        )
        return


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
        self._setGenerators()
        return

    def place(self, editor: Editor) -> None:
        """ Place all blocks of the tower roof access point in Minecraft. """
        
        editor.placeBlock(self.uShapeGenerator, self.baseM)
        
        editor.placeBlock(
            self.ladderGenerator,
            Block('ladder', {'facing': self.facing})
        )

        self.stairM.setFacing(self.facing)
        for stairGenerator in [self.stairGenerator1, self.stairGenerator2]:
            editor.placeBlock(stairGenerator, self.stairM)
        # stairs set 3 is placed in the opposite direction of self.facing
        self.stairM.setFacing({'east': 'west', 'west': 'east'}[self.facing])
        editor.placeBlock(self.stairGenerator3, self.stairM)
        
        editor.placeBlock(self.gateGenerator, self.gateM)
        for gapGenerator in [self.gapGenerator1, self.gapGenerator2]:
            editor.placeBlock(gapGenerator, Air)
        
        return

    def _setGenerators(self) -> None:
        """ Determine the locations of all blocks of the roof access. """
        self.uShapeGenerator = cuboid3D(
            corner1 = self.o + ivec3(self.xSign * +0, -1, -4),
            corner2 = self.o + ivec3(self.xSign * +1, -1, +4)
        )
        self.ladderGenerator = cuboid3D(
            corner1 = self.o + ivec3(0, -self.roomH+1, -1),
            corner2 = self.o + ivec3(0,            -1, +1)
        )
        self.stairGenerator1 = line3D(
            begin = self.o + ivec3(self.xSign* +1, -1, -1),
            end   = self.o + ivec3(self.xSign* +1, -1, +1)
        )
        self.stairGenerator2 = line3D(
            begin = self.o + ivec3(self.xSign* +2, 0, -1),
            end   = self.o + ivec3(self.xSign* +2, 0, +1)
        )
        self.stairGenerator3 = line3D(
            begin = self.o + ivec3(self.xSign* -1, 0, -1),
            end   = self.o + ivec3(self.xSign* -1, 0, +1)
        )
        self.gateGenerator = cuboid3D(
            corner1 = self.o + ivec3(self.xSign* +0, +1, -2),
            corner2 = self.o + ivec3(self.xSign* +2, +3, +2)
        )
        self.gapGenerator1 = cuboid3D(
            corner1 = self.o + ivec3(self.xSign* +0, +1, -1),
            corner2 = self.o + ivec3(self.xSign* +2, +2, +1)
        )
        self.gapGenerator2 = cuboid3D(
            corner1 = self.o + ivec3(self.xSign* +0, 0, -1),
            corner2 = self.o + ivec3(self.xSign* +1, 0, +1)
        )
        return

    @property
    def facing(self) -> str:
        return {'mm': 'east', 'mp': 'east', 'pp': 'west', 'pm': 'west'}[self.district]

    @property
    def xSign(self) -> int:
        return {'east': +1, 'west': -1}[self.facing]


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
        district: one of 'mm', 'mp', 'pp', 'pm' (see README.md)
        base: TowerBase instance
        room: TowerRoom instance
        roof: TowerRoof instance
        roofAccess: TowerRoofAccess instance

        ! Note: tower.o(rigin) is set to room.o(rigin) !
        """
        assert district in ['mm', 'mp', 'pp', 'pm'], f'Invalid district: {district}'
        self.district = district

        self.base = base
        self.room = room
        self.roof = roof
        self.roofAccess = roofAccess
        self.o = self.room.o
        self.entrancePoints = []
        return

    def place(self, editor: Editor) -> None:
        """ Place the tower in Minecraft. """
        self.base.place(editor)
        self.room.place(editor)
        self.roof.place(editor)
        self._addEntrances(editor)
        self.roofAccess.place(editor)
        return

    @property
    def entranceDirections(self) -> list[str]:
        """ Each tower has a unique set of 2 entrance directions, depending on its district. """
        return {
            'mm': ['pz', 'px'],
            'mp': ['mz', 'px'],
            'pp': ['mz', 'mx'],
            'pm': ['pz', 'mx']
        }[self.district]

    def _addEntrances(self, editor: Editor) -> None:
        """ Add the correct entrances to the tower. """
        for direction in ['pz', 'mz', 'px', 'mx']:
            if direction in self.entranceDirections:
                entrancePos: ivec3 = self._findEntrance(direction)
                setattr(self, f'entrance{direction.upper()}', entrancePos)
            else:
                setattr(self, f'entrance{direction.upper()}', None)
        editor.placeBlock(self.entrancePoints, Air)
        return

    def _findEntrance(self, direction: str) -> ivec3:
        """
        Adds an entrance to the tower by carving out
        a 3x4x1 area in the wall of the main room.
        
        It returns the origin position of the entrance.
        """

        def _placeEntrance(x1: int, x2: int, z1: int, z2: int) -> None:
            """ helper method """
            self.entrancePoints.extend(cuboid3D(
                corner1 = self.o + ivec3(x1, 1, z1),
                corner2 = self.o + ivec3(x2, 4, z2)
            ))
        
        r = self.room.radius

        if direction == 'pz':
            _placeEntrance(-1, 1, r, r)
            return self.o + ivec3(0, -1, r)
        elif direction == 'mz':
            _placeEntrance(-1, 1, -r, -r)
            return self.o + ivec3(0, -1, -r)
        elif direction == 'px':
            _placeEntrance(r, r, -1, 1)
            return self.o + ivec3(r, -1, 0)
        elif direction == 'mx':
            _placeEntrance(-r, -r, -1, 1)
            return self.o + ivec3(-r, -1, 0)
        else:
            raise ValueError(f'Invalid direction: {direction}')
