#!/usr/bin/env python3

from typing import Generator

from gdpc import geometry, Block
from glm import ivec3
from gdpc.vector_tools import fittingCylinder, Y, cuboid3D, line3D


def pyramid(origin: ivec3, height: int, hollow: bool = False) -> Generator[ivec3, None, None]:
    """
    Generate the positions for the blocks of a pyramid.

    Params:
    - height (int): the height of the pyramid
    - hollow (bool): whether the pyramid should be hollow or not
    
    The base width will be `2 * height - 1`.
    For example, the heightmap of a pyramid with height 3 will look like this:
    ```
        1 1 1 1 1
        1 2 2 2 1
        1 2 3 2 1
        1 2 2 2 1
        1 1 1 1 1
    ```
    """
    for y in range(height):
        from_ = -height + y + 1
        to_   = +height - y
        for x in range(from_, to_):
            for z in range(from_, to_):
                if hollow and not (abs(x) == to_-1 or abs(z) == to_-1):
                    continue
                yield origin + ivec3(x, y, z)


def cone(origin: ivec3, height: int, hollow: bool = False) -> Generator[ivec3, None, None]:
    """
    Generate the positions for the blocks of a cone.

    Params:
    - height (int): the height of the cone
    - hollow (bool): whether the cone should be hollow or not
    
    The base width (diameter) will be `2 * height - 1`.
    For example, the heightmap of a cone with height 3 will look like this:
    ```
        0 1 1 1 0
        1 1 2 1 1
        1 2 3 2 1
        1 1 2 1 1
        0 1 1 1 0
    ```
    """
    allPoints = []

    for y in range(height):
        from_ = origin + (-height + y + 1, y, -height + y + 1)
        to_   = origin + (+height - y - 1, y, +height - y - 1)
        points = [point for point in fittingCylinder(from_, to_)]
        allPoints.extend(points)
    
    # if hollow, remove points that have a point directly above them
    if hollow:
        allPointsCopy = set(allPoints)
        allPoints = [point for point in allPoints if not point + Y in allPointsCopy]

    yield from allPoints
                
def triangle(origin: ivec3, size: int, direction: str) -> Generator[ivec3, None, None]:
    """
    Generate the positions for the blocks of an isosceles triangle in the xz plane.

    Params:
    - size (int): the size of the triangle sides (including origin)
    - direction (str): the directions in which to extend the triangle
    """
    assert direction in ['nw', 'ne', 'sw', 'se']
    xSign, zSign = {'nw': (-1, -1), 'ne': (+1, -1), 'sw': (-1, +1), 'se': (+1, +1)}[direction]
    for x in range(size):
        for z in range(size-x):
                yield origin + ivec3(x * xSign, 0, z * zSign)
