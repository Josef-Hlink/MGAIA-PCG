#!/usr/bin/env python3

import os
from time import perf_counter

import numpy as np

from gdpc.vector_tools import addY
from gdpc import Block

from helper import getEditor, getBuildArea, clearBuildArea, createOverview
from buildings import Tower
from builders import buildBounds, buildTowers, buildRoads


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
    base = np.min(heightMap)
    height = np.max(heightMap) - base
    center = addY(buildRect.center, base)

    # excavate if necessary
    if height > 10:
        start = perf_counter()
        clearBuildArea(editor, center, height = height)
        print(f'Clearing build area took {perf_counter() - start:.2f} seconds.')

    # define default block palette
    palette: list[Block] = [
        Block(id)
        for id in 
            10 * ['stone_bricks'] +
            5 * ['cracked_stone_bricks'] +
            2 * ['mossy_stone_bricks']
    ]

    # place red blocks to visualize bounds of build area
    start = perf_counter()
    buildBounds(editor, buildRect, y = base)
    print(f'Building bounds took {perf_counter() - start:.2f} seconds.')

    # build towers
    start = perf_counter()
    towers: dict[str, Tower] = buildTowers(editor, buildRect, y = base, palette = palette)
    print(f'Building towers took {perf_counter() - start:.2f} seconds.')

    # build roads between towers
    start = perf_counter()
    buildRoads(editor, towers, palette = palette)
    print(f'Building roads took {perf_counter() - start:.2f} seconds.')

    # hollow towers to clear the mess left by road construction
    start = perf_counter()
    for tower in towers.values():
        tower.hollow(editor)
    print(f'Hollowing towers took {perf_counter() - start:.2f} seconds.')

    # create overview image with matplotlib
    createOverview(editor, buildRect)
    print('Created overview.png')


if __name__ == '__main__':
    main()
