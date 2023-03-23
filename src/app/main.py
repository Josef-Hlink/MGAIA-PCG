#!/usr/bin/env python3

import os
import sys
from time import perf_counter, strftime, gmtime

import numpy as np

from gdpc.vector_tools import addY
from glm import ivec3

from structs.tower import Tower
from structs.castle import Castle
from builders import buildBounds, buildTowers, buildCastle, buildBridges, buildEntryPoints, buildInteriors
from helper import getEditor, getBuildArea, createOverview


def main():

    os.chdir(os.path.dirname(__file__))

    editor = getEditor()
    buildArea = getBuildArea(editor)
    buildRect = buildArea.toRect()

    worldSlice = editor.loadWorldSlice(buildRect)

    heightMaps: tuple[np.ndarray] = (worldSlice.heightmaps['OCEAN_FLOOR'], worldSlice.heightmaps['MOTION_BLOCKING_NO_LEAVES'])
    base = np.max(heightMaps[1])

    start = perf_counter()

    if len(sys.argv) > 1 and sys.argv[1] == '--dev':
        buildBounds(editor, buildRect, base)

    absoluteCenter: ivec3 = addY(buildRect.center, base)

    towers: dict[str, Tower] = buildTowers(editor, absoluteCenter, heightMaps)

    relativeCenter = sum([tower.o for tower in towers.values()]) / 4
    
    castle: Castle = buildCastle(editor, relativeCenter, absoluteCenter, heightMaps)

    buildBridges(editor, towers)

    buildEntryPoints(editor, castle, towers)

    buildInteriors(editor, towers)

    end = perf_counter()
    formattedTime = strftime('%M:%S', gmtime(end - start))
    print(f'\nFinished all structures in {formattedTime} min')

    createOverview(editor, buildRect)
    print('\nCreated overview.png')


if __name__ == '__main__':
    main()
