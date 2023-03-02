#!/usr/bin/env python3

from time import perf_counter
from helper import getEditor, getBuildArea
import matplotlib.pyplot as plt


def main():
    
    editor = getEditor()
    buildArea = getBuildArea(editor)

    start = perf_counter()
    worldSlice = editor.loadWorldSlice(buildArea.toRect())
    print(f'Getting world slice took {perf_counter() - start:.2f} seconds.')

    heightMap = worldSlice.heightmaps['MOTION_BLOCKING_NO_LEAVES']
    plt.imshow(heightMap)
    plt.show()

    pass


if __name__ == '__main__':
    main()