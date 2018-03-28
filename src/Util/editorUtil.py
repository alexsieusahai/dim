import os

from dataStructures.lineNode import LineNode

def currentLineHeight(editorObj):
    """
    Returns the height of the current line
    """
    return lineHeight(editorObj, editorObj.currentLine)

def lineHeight(editorObj, lineNode):
    """
    Returns the "height" (how many rows it takes up) of lineNode object passed in
    """
    manyLines = len(lineNode.value)//editorObj.editorscr.getmaxyx()[1]+1
    return manyLines if manyLines else 1

def getCurrentChar(editorObj):
    return editorObj.currentLine.value[editorObj.currentLineIndex]

def getNextChar(editorObj):
    # note we are guaranteed to have this as we never get to newline char
    return editorObj.currentLine.value[editorObj.currentLineIndex+1]


def moveToEndOfLine(editorObj):
    editorObj.currentLineIndex = len(editorObj.currentLine.value)-2

def moveToBeginningOfLine(editorObj):
    editorObj.currentLineIndex = 0

def deleteLine(editorObj,lineNode):
    """
    Deletion looks like this:
    ... -> lineNode.lastNode -> lineNode -> lineNode.nextNode -> ...
    to
    ... -> lineNode.lastNode -> lineNode.nextNode -> ...
    """

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
    return returnNode

def insertLine(editorObj,lineNode):
    """
    Inserts a line just like how vim does
    ... -> lineNode.lastNode -> lineNode -> lineNode.nextNode -> ...
    ... -> lineNode.lastNode -> lineNode -> newNode -> lineNode.nextNode -> ...
    """

    newLineValue = editorObj.currentLine.value[editorObj.currentLineIndex:]
    editorObj.currentLine.value = editorObj.currentLine.value[:editorObj.currentLineIndex]+'\n'
    newNode = LineNode(newLineValue,editorObj.currentLine)

    temp = lineNode.nextNode # save it for later
    lineNode.nextNode = newNode
    newNode.nextNode = temp
    if temp != None:
        temp.lastNode = newNode

    editorObj.lineLinkedList.length += 1

    editorObj.drawLines()

    return newNode

def getCmd(editorObj,getSearch=False):
    """
    Get command from user when in command mode
    """
    cmdStr = ':'
    if getSearch:
        cmdStr = '?'
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

def getDirs(self):
    dirs = ['..']+sorted(os.listdir())
    i = 1
    for directory in dirs[1:]:
        if '.' == directory[0]:
            dirs.pop(i)
            i -= 1
        i += 1
    return dirs


