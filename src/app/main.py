#!/usr/bin/env python3

import os
from time import perf_counter

import numpy as np

from gdpc.vector_tools import addY
from glm import ivec3

from structs.tower import Tower
from structs.bigtree import BigTree
from structs.castle import Castle
from structs.bridge import Bridge
from builders import buildBounds, buildTowers, buildCastle, buildBigTree, buildBridges
from helper import getEditor, getBuildArea, createOverview


def main():
    # change cwd to src
    os.chdir(os.path.dirname(__file__))

    # get editor object and build area to work with
    editor = getEditor()
    buildArea = getBuildArea(editor)
    buildRect = buildArea.toRect()

    # load world slice
    start = perf_counter()
    worldSlice = editor.loadWorldSlice(buildRect)
    print(f'Getting world slice took {perf_counter() - start:.2f} seconds.')

    # get height map and define center
    heightMap: np.ndarray = worldSlice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    base = np.max(heightMap)

    # place red blocks to visualize bounds of build area
    start = perf_counter()
    buildBounds(editor, buildRect, y = base)
    print(f'Building bounds took {perf_counter() - start:.2f} seconds.')

    center: ivec3 = addY(buildRect.center, base)

    # place towers
    start = perf_counter()
    towers: dict[str, Tower] = buildTowers(editor, center)
    print(f'Building towers took {perf_counter() - start:.2f} seconds.')

    relativeCenter = sum([tower.o for tower in towers.values()]) / 4
    
    # place castle
    start = perf_counter()
    castle: Castle = buildCastle(editor, relativeCenter)
    print(f'Building castle took {perf_counter() - start:.2f} seconds.')
    
    # place big tree inside castle
    start = perf_counter()
    bigTree: BigTree = buildBigTree(editor, relativeCenter)
    print(f'Building big tree took {perf_counter() - start:.2f} seconds.')

    # build bridges between towers' entrances
    start = perf_counter()
    bridges: list[Bridge] = buildBridges(editor, towers)
    print(f'Building bridges took {perf_counter() - start:.2f} seconds.')

    # create overview image with matplotlib
    createOverview(editor, buildRect)
    print('Created overview.png')


if __name__ == '__main__':
    main()
