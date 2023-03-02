#!/usr/bin/env python3

"""
Helper functions to make main.py more readable.
"""

import sys

from gdpc import __url__, Editor, Box
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError


def getEditor() -> Editor:
    """ Instantiate an Editor object and check if it can connect to the GDMC HTTP interface. """
    
    editor = Editor()

    try:
        editor.checkConnection()
    except InterfaceConnectionError:
        print(
            f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
            "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
            "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
            f"See {__url__}/README.md for more information."
        )
        sys.exit(1)

    return editor

def getBuildArea(editor: Editor) -> Box:
    """ Get the build area and check if it is set. """
    
    try:
        buildArea = editor.getBuildArea()
    except BuildAreaNotSetError:
        print(
            "Error: failed to get the build area!\n"
            "Make sure to set the build area with the /setbuildarea command in-game.\n"
            "For example: /setbuildarea ~0 ~0 ~0 ~100 ~100 ~100"
        )
        sys.exit(1)

    return buildArea

