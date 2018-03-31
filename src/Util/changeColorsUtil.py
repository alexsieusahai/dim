import curses  # for the color selector
import os

from dataStructures.lineLinkedList import LineLinkedList
import Util.editorUtil as editorUtil
import movement.editorMovement as editorMovement

def displayThemes(editorObj, dimDir):
    os.chdir(dimDir+'/themes')

    editorObj.lineLinkedList = LineLinkedList(os.listdir())
    editorObj.currentLine = editorObj.topLine = editorObj.lineLinkedList.start
    editorObj.drawLines(editorObj.editorscr, editorObj.topLine)
    editorObj.drawLineNumbers()
    editorObj.editorscr.refresh()

    while True:
        c = chr(editorObj.editorscr.getch())
        if c == 'j':
            editorMovement.moveDown(editorObj)
        if c == 'k':
            editorMovement.moveUp(editorObj)
        if c == chr(10):  # enter
            return editorObj.currentLine.value
        if c == chr(27):  # escape
            break
        editorObj.drawLineNumbers()
        editorObj.editorscr.refresh()

def changeColorsUI(editorObj, backgroundKey):
    raise NotImplementedError
    """
    backgroundKey is the key for the background color
    currently being used in the editor

    Opens up a curses interface for the user
    to pick the colors for each type of token as
    defined in syntaxHighlighting.py by displaying all
    the possible colors and telling the user what
    the user is picking it for. The user then gets a sample
    display of some file with the syntax applied, and is prompted
    with a yes/no to save the syntax with some specified filename
    and load it.
    """
    editorObj.editorscr.clear()
    editorObj.lineLinkedList = LineLinkedList(['A'])
    editorObj.topLine = editorObj.currentLine = editorObj.lineLinkedList.start
    editorUtil.insertLine(editorObj, editorObj.currentLine)
    editorObj.drawLines(editorObj.editorscr, editorObj.topLine)

    # don't have to save anything for later since the only time where
    # we call this, we are in options from before so we'll retrieve everything
    # on the way out of this function

    ref = 50
    for i in range(0, 1000, 200):
        for j in range(0, 1000, 200):
            for k in range(0, 1000, 200):
                curses.init_color(ref, i, j, k)
                curses.init_pair(ref, ref, backgroundKey)
                #editorObj.editorscr.addstr('A', curses.color_pair(ref))
                editorObj.currentLine.value = (
                        editorObj.currentLine.value[:-1] + 'A' + '\n')
                editorObj.currentLine.colors.append(ref)
                ref += 1
    editorObj.drawLines(editorObj.editorscr, editorObj.topLine)

    # getcmd for the name
    editorObj.editorscr.getch()

    return 'default.json'


