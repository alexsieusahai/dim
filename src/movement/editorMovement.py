import Util.editorUtil as editorUtil

def moveDown(editorObj):
    """
    Moves down one line
    """
    y = editorObj.editorscr.getyx()[0]
    if editorObj.currentLine.nextNode is None:  # we don't have any more nodes
        return
    currentLineHeight = editorUtil.lineHeight(editorObj.editorscr, editorObj.currentLine)
    if y + currentLineHeight < editorObj.editorscr.getmaxyx()[0]-2:
        editorObj.currentLine = editorObj.currentLine.nextNode
        if editorObj.currentLineIndex > len(editorObj.currentLine.value) - 2:
            editorObj.currentLineIndex = len(editorObj.currentLine.value) - 2
        if editorObj.currentLineIndex < 0:
            editorObj.currentLineIndex = 0

    elif editorObj.currentLine.nextNode is not None:
        editorObj.currentLine = editorObj.currentLine.nextNode
        amountToMoveDown = editorUtil.lineHeight(editorObj.editorscr, editorObj.currentLine)
        while amountToMoveDown > 0:
            amountToMoveDown -= editorUtil.lineHeight(editorObj.editorscr, editorObj.topLine)
            editorObj.topLine = editorObj.topLine.nextNode
            editorObj.topLineCount += 1

    # redraw everything
    editorObj.drawLines(editorObj.editorscr, editorObj.topLine)
    editorObj.drawLineNumbers()

def moveUp(editorObj):
    #if editorObj.editorscr.getyx()[0] > 0:
    if editorObj.currentLine is not editorObj.topLine:
        editorObj.currentLine = editorObj.currentLine.lastNode
        if editorObj.currentLineIndex > len(editorObj.currentLine.value) - 2:
            editorObj.currentLineIndex = len(editorObj.currentLine.value) - 2
            if editorObj.currentLineIndex < 0:
                editorObj.currentLineIndex = 0
    elif editorObj.currentLine.lastNode is not None:
        editorObj.currentLine = editorObj.currentLine.lastNode
        editorObj.topLine = editorObj.topLine.lastNode
        editorObj.topLineCount -= 1
        editorObj.drawLineNumbers()

def moveLeft(editorObj):
    if editorObj.editorscr.getyx()[1] > 0:
        if editorObj.currentLineIndex > len(editorObj.currentLine.value)-2:
            editorObj.currentLineIndex = len(editorObj.currentLine.value)-2
        if editorObj.currentLineIndex > 0:
            editorObj.currentLineIndex -= 1
    else:
        if editorObj.currentLineIndex > 0:
            editorObj.currentLineIndex -= 1

def moveRight(editorObj):
    if editorObj.currentLine.value != '\n':  # if it's only newline ignore
        if editorObj.currentLineIndex > len(editorObj.currentLine.value) - 2:
            editorObj.currentLineIndex = len(editorObj.currentLine.value) - 2

        if editorObj.currentLine.value[editorObj.currentLineIndex+1] != '\n':
            editorObj.currentLineIndex += 1
