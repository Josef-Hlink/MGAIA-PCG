#!/usr/bin/env python3

"""
Builder functions to make main.py more readable.
"""

from gdpc import Block, geometry, Editor, Box
from glm import ivec3
from gdpc.vector_tools import addY


class Tower:

    def __init__(
            self,
            origin: ivec3,
            material: Block | list[Block],
            heights: list[int],
            radii: list[int],
            district: str
        ) -> None:

        assert len(heights) == len(radii) == 2

        self.origin = origin
        self.material = material
        self.heights = heights
        self.radii = radii
        self.district = district
        return

    def build(self, editor: Editor) -> None:
        for i in range(2):
            height, radius = self.heights[i], self.radii[i]
            baseY = 0 if i == 0 else self.heights[0]
            geometry.placeFittingCylinder(
                editor,
                self.origin + ivec3(-radius, baseY, -radius),
                self.origin + ivec3(radius, baseY + height, radius),
                self.material,
                tube = not i,
                hollow = i
            )

    def hollow(self, editor: Editor) -> None:
        geometry.placeFittingCylinder(
            editor,
            self.origin + ivec3(-self.radii[1]+1, self.heights[0]+1, -self.radii[1]+1),
            self.origin + ivec3(self.radii[1]-1, self.heights[0] + self.heights[1]-1, self.radii[1]-1),
            Block('air')
        )
