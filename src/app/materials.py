#!/usr/bin/env python3

"""
All materials will be defined here, so palettes as well as single blocks.
"""

from typing import Sequence, Optional
from gdpc import Block
from gdpc.minecraft_tools import signBlock


class Palette:
    """ A palette is a sequence of blocks. """
    def __init__(self, blocks: Sequence[Block]):
        self.blocks = blocks

    def __iter__(self):
        return iter(self.blocks)


basePalette = [Block(id) for id in 
    7 * ['stone_bricks'] +
    2 * ['cracked_stone_bricks'] +
    1 * ['mossy_stone_bricks']
]
class BasePalette(Palette):
    """
    70% stone bricks,
    20% cracked stone bricks,
    10% mossy stone bricks
    """
    def __init__(self):
        super().__init__(basePalette)

baseSlabPalette = [Block(id) for id in
    8 * ['stone_brick_slab'] +
    2 * ['mossy_stone_brick_slab']
]
class BaseSlabPalette(Palette):
    """
    80% stone brick slabs,
    20% mossy stone brick slabs
    """
    def __init__(self, type: str = 'bottom'):
        super().__init__(baseSlabPalette)
        self.setType(type)

    def setType(self, type: str):
        for block in self.blocks:
            block.states['type'] = type


baseStairPalette = [Block(id) for id in
    8 * ['stone_brick_stairs'] +
    2 * ['mossy_stone_brick_stairs']
]
class BaseStairPalette(Palette):
    """
    80% stone brick stairs,
    20% mossy stone brick stairs
    """
    def __init__(self):
        super().__init__(baseStairPalette)
        self.setHalf('bottom')

    def setFacing(self, facing: str):
        for block in self.blocks:
            block.states['facing'] = facing
    
    def setHalf(self, half: str):
        for block in self.blocks:
            block.states['half'] = half

randomColorGlassPalette = [Block(f'{color}_stained_glass') for color in
    ['white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray',
     'light_gray', 'cyan', 'purple', 'blue', 'brown', 'green', 'red', 'black']
]
class RandomColorGlassPalette(Palette):
    """
    completely random color stained glass
    """
    def __init__(self):
        super().__init__(randomColorGlassPalette)


class Concrete:
    """ A simple colored concrete block. """
    def __init__(self, color: str):
        self.block = Block(f'{color}_concrete')

    def __iter__(self):
        return iter([self.block])

class PurpurStairs:
    """ A simple purpur stairs block. """
    def __init__(self):
        self.block = Block('purpur_stairs', {'facing': 'north', 'half': 'bottom'})

    def setFacing(self, facing: str):
        self.block.states['facing'] = facing

    def setHalf(self, half: str):
        self.block.states['half'] = half

    def __iter__(self):
        return iter([self.block])


Air = Block('air')
Netherite = Block('netherite_block')
Diamond = Block('diamond_block')
Beacon = Block('beacon')
Glass = Block('glass')
IronBars = Block('iron_bars')
GlowStone = Block('glowstone')
CryingObsidian = Block('crying_obsidian')
TintedGlass = Block('tinted_glass')
SpruceLeaves = Block('spruce_leaves')
EndStoneBricks = Block('end_stone_bricks')
EndStoneBrickWall = Block('end_stone_brick_wall')
Magma = Block('magma_block')


Chain = Block('chain')
Lantern = Block('lantern', {'hanging': 'true'})
SoulLantern = Block('soul_lantern', {'hanging': 'true'})

def pot(plant: str) -> Block:
    return Block(f'potted_{plant}')


SpruceLog = Block('spruce_log', {'axis': 'y'})

Water = Block('water')
Lava = Block('lava')
