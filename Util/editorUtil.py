from dataStructures.lineNode import LineNode

def currentLineHeight(editorObj):
    """
    Returns the height of the current line
    """
    return editorObj.lineHeight(self.currentLine)

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

def deleteLine(self,lineNode):
    """
    Deletion looks like this:
    ... -> lineNode.lastNode -> lineNode -> lineNode.nextNode -> ...
    to
    ... -> lineNode.lastNode -> lineNode.nextNode -> ...
    """

    self.currentLineIndex = len(lineNode.lastNode.value)-1
    lineNode.lastNode.value = lineNode.lastNode.value[:-1]+lineNode.value[:-1]+'\n'
    lineNode.lastNode.colors = lineNode.lastNode.colors[:-1]+lineNode.colors
    lineNode.lastNode.nextNode = lineNode.nextNode
    # handle edge case
    if lineNode.nextNode != None:
        lineNode.nextNode.lastNode = lineNode.lastNode
    returnNode = lineNode.lastNode
    del lineNode
    self.lineLinkedList.length -= 1
    return returnNode

def insertLine(self,lineNode):
    """
    Inserts a line just like how vim does
    ... -> lineNode.lastNode -> lineNode -> lineNode.nextNode -> ...
    ... -> lineNode.lastNode -> lineNode -> newNode -> lineNode.nextNode -> ...
    """

    newLineValue = self.currentLine.value[self.currentLineIndex:]
    self.currentLine.value = self.currentLine.value[:self.currentLineIndex]+'\n'
    newNode = LineNode(newLineValue,self.currentLine)

    temp = lineNode.nextNode # save it for later
    lineNode.nextNode = newNode
    newNode.nextNode = temp
    if temp != None:
        temp.lastNode = newNode

    self.lineLinkedList.length += 1

    self.drawLines()

    return newNode

