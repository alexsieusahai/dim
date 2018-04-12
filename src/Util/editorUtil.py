import os  # to get the dirs

from dataStructures.lineNode import LineNode
import Util
import movement

import algorithms.kmp as kmp

def lineHeight(scr, lineNode):
    """
    Returns the "height" (how many rows it takes up) of lineNode object passed in
    Doesn't work properly rn
    """
    if lineNode is None:
        return 0
    manyLines = (len(lineNode.value)+1)//scr.getmaxyx()[1]+1
    # above solution doesn't account for tabs
    return manyLines

def getCurrentChar(editorObj):
    return editorObj.currentLine.value[editorObj.currentLineIndex]

def getNextChar(editorObj):
    # note we are guaranteed to have this as we never get to newline char
    return editorObj.currentLine.value[editorObj.currentLineIndex+1]

def moveToEndOfLine(editorObj):
    editorObj.currentLineIndex = len(editorObj.currentLine.value)-2

def moveToBeginningOfLine(editorObj):
    editorObj.currentLineIndex = 0

def deleteCharacter(editorObj, lineNode, index):
    """
    Delete character in lineNode.value at index i
    """
    if index > len(lineNode.value)-2:  # ignore newline
        if editorObj.currentLine.nextNode is None:
            return
        editorObj.currentLine = deleteLine(editorObj, lineNode).nextNode
        editorObj.currentLineIndex = 0
    else:
        lineNode.value = lineNode.value[:index]+lineNode.value[index+1:]
        editorObj.currentLineIndex = min(editorObj.currentLineIndex,
                                        len(lineNode.value))

def deleteLine(editorObj, lineNode, trueDelete=False):
    """
    Deletion looks like this:
    ... -> lineNode.lastNode -> lineNode -> lineNode.nextNode -> ...
    to
    ... -> lineNode.lastNode -> lineNode.nextNode -> ...
    """

    if lineNode.lastNode is not None:
        if trueDelete:
            editorObj.currentLineIndex = 0
            lineNode.lastNode.value = lineNode.lastNode.value
        else:
            editorObj.currentLineIndex = len(lineNode.lastNode.value)-1
            lineNode.lastNode.value = lineNode.lastNode.value[:-1]+lineNode.value[:-1]+'\n'
        lineNode.lastNode.colors = lineNode.lastNode.colors[:-1]+lineNode.colors
        lineNode.lastNode.nextNode = lineNode.nextNode
        # handle edge case
        if lineNode.nextNode != None:
            lineNode.nextNode.lastNode = lineNode.lastNode
        returnNode = lineNode.lastNode
        del lineNode
        editorObj.lineLinkedList.length -= 1

        if trueDelete:
            return returnNode.nextNode
        return returnNode
    editorObj.currentLineIndex = 0
    return lineNode  # don't do anything

def insertLine(editorObj, lineNode, cleanInsert=False):
    """
    Inserts a line just like how vim does
    ... -> lineNode.lastNode -> lineNode -> lineNode.nextNode -> ...
    ... -> lineNode.lastNode -> lineNode -> newNode -> lineNode.nextNode -> ...
    """
    if cleanInsert:
        newLineValue = '\n'
    else:
        newLineValue = editorObj.currentLine.value[editorObj.currentLineIndex:]
        editorObj.currentLine.value = editorObj.currentLine.value[:editorObj.currentLineIndex]+'\n'
    newNode = LineNode(newLineValue, editorObj.currentLine)
    # lastNode of newNode is set to editorObj.currentLine

    # check to see if it's at the bottom of the screen
    if editorObj.editorscr.getyx()[0] + 1 > editorObj.editorscr.getmaxyx()[0] - 2:
        editorObj.topLineCount += 1

    temp = lineNode.nextNode  # save it for later,
    lineNode.nextNode = newNode # since we're overwriting lineNode.nextNode
    newNode.nextNode = temp
    if temp != None:
        temp.lastNode = newNode

    editorObj.lineLinkedList.length += 1

    Util.drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)

    return newNode

def getCmd(editorObj,altDisplayChar=''):
    """
    Get command from user using the command line window
    """
    cmdStr = ':'
    if altDisplayChar:
        cmdStr = altDisplayChar
    c = ''
    while c != '\n':
        if c == chr(127): # backspace
            cmdStr = cmdStr[:-1]
        elif c == chr(27): # escape
            return chr(27)
        else:
            cmdStr += c

        editorObj.cmdlinescr.clear()
        editorObj.cmdlinescr.addstr(cmdStr)
        editorObj.cmdlinescr.refresh()
        c = chr(editorObj.cmdlinescr.getch())
    return cmdStr

def getDirs():
    dirs = ['..']+sorted(os.listdir())
    i = 1
    for directory in dirs[1:]:
        if '.' == directory[0]:
            dirs.pop(i)
            i -= 1
        i += 1
    return dirs

def find_pattern_in_syntax(editorObj, pattern_to_find):
    if pattern_to_find[0] == '/':
        pattern_to_find = pattern_to_find[1:]
    walk = editorObj.lineLinkedList.start
    matchBuffer = []
    lineNumber = 1
    while walk is not None:
        matches = kmp.kmp(walk.value, pattern_to_find)
        if matches:
            for match in matches:
                matchBuffer.append((lineNumber, match))
        walk = walk.nextNode
        lineNumber += 1
    return matchBuffer

def move_to_node_and_index(editorObj, lineNumber, lineIndex):
    editorObj.currentLine = editorObj.topLine = editorObj.lineLinkedList.start
    for i in range(lineNumber-1):
        movement.editorMovement.moveDown(editorObj)
        Util.drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
        editorObj.drawLineNumbers()
    editorObj.currentLineIndex = lineIndex


