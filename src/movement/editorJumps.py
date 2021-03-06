import string

import Util.editorUtil as editorUtil
import Util.drawUtil as drawUtil
import movement.editorMovement as editorMovement

def jump_forward_one_word(editorObj, repeats, index):
    """
    Walk through elements on line until you hit
    either punctuation (where you stop) or spaces
    If editorObj.deleteMode is True then delete instead of move
    """
    for i in range(repeats):

        # handle edge case of `w` on '\n' line
        if editorUtil.getCurrentChar(editorObj) == '\n':
            if editorObj.deleteMode is True:
                editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                drawUtil.drawLineNumbers(editorObj)
            else:
                editorMovement.moveDown(editorObj)
                editorObj.currentLineIndex = 0
            continue

        if editorUtil.getNextChar(editorObj) == '\n':
            if editorObj.deleteMode is True:
                editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
            else:
                editorMovement.moveDown(editorObj)
                editorObj.currentLineIndex = 0
            continue

        while True:

            if editorObj.deleteMode is True:
                editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
            else:
                editorMovement.moveRight(editorObj)
            drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
            drawUtil.drawLineNumbers(editorObj)
            c = editorUtil.getCurrentChar(editorObj)

            if c in editorObj.punctuationChars:
                break

            if editorUtil.getNextChar(editorObj) == '\n':
                if editorObj.deleteMode is True:
                    editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                    editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                else:
                    editorMovement.moveDown(editorObj)
                    editorObj.currentLineIndex = 0
                drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
                drawUtil.drawLineNumbers(editorObj)
                break

            if c == ' ':
                while c == ' ':
                    if editorObj.deleteMode is True:
                        editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                    else:
                        editorMovement.moveRight(editorObj)
                    drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
                    drawUtil.drawLineNumbers(editorObj)
                    c = editorUtil.getCurrentChar(editorObj)
                    if editorUtil.getNextChar(editorObj) == '\n':
                        break
                break

def jump_one_word_and_whitespace(editorObj, repeats, index):
    """
    Walk through elements on line until you hit
    either punctuation (where you stop) or spaces
    (where you walk through until you hit something that isn't a space)
    If editorObj.deleteMode is True then delete instead of move
    """
    for i in range(repeats):

        # handle edge case of `e` on '\n' line
        if editorObj.currentLine.value == '\n' or editorUtil.getNextChar(editorObj) == '\n':
            if editorObj.deleteMode is True:
                if editorObj.currentLine.value == '\n':
                    editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                else:
                    editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                    editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
                continue

            editorMovement.moveDown(editorObj)
            editorObj.currentLineIndex = 0
            continue

        if editorObj.deleteMode is True:
            editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
        else:
            editorMovement.moveRight(editorObj)

        while editorUtil.getNextChar(editorObj) == ' ':
            if editorObj.deleteMode is True:
                editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
            else:
                editorMovement.moveRight(editorObj)
        while editorUtil.getNextChar(editorObj) in string.ascii_letters:
            if editorObj.deleteMode is True:
                editorUtil.deleteCharacter(editorObj, editorObj.currentLine, index)
            else:
                editorMovement.moveRight(editorObj)

def jump_backward_one_word(editorObj, repeats, index):
    """
    Walk through elements on the line backwards
    until the character before is punctuation or a space
    If editorObj.deleteMode is True then delete instead of move
    """
    for i in range(repeats):

        moveForward = True
        editorMovement.moveLeft(editorObj)
        editorObj.currentLineIndex -= 1
        if editorObj.currentLineIndex < 0:
            if editorObj.currentLine.lastNode is None:
                editorObj.currentLineIndex = 0
                continue
            editorMovement.moveUp(editorObj)
            editorUtil.moveToEndOfLine(editorObj)
            drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
            drawUtil.drawLineNumbers(editorObj)
            editorObj.currentLineIndex = 0

        if len(editorObj.currentLine.value) <= 2:
            continue

        # now we are guaranteed a line
        # with at least two characters
        c = editorUtil.getCurrentChar(editorObj)

        while c == ' ':
            editorMovement.moveLeft(editorObj)
            drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
            drawUtil.drawLineNumbers(editorObj)
            c = editorUtil.getCurrentChar(editorObj)
            if c in editorObj.punctuationChars:
                moveForward = False
                break
            if editorObj.editorscr.getyx()[1] == 0:
                if editorObj.currentLine == 0:
                    moveForward = False
                    break
                editorMovement.moveUp(editorObj)
                drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
                drawUtil.drawLineNumbers(editorObj)
                editorUtil.moveToEndOfLine(editorObj)
                drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
                drawUtil.drawLineNumbers(editorObj)

        while c in string.ascii_letters or c in string.digits:
            editorMovement.moveLeft(editorObj)
            drawUtil.drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
            drawUtil.drawLineNumbers(editorObj)
            c = editorUtil.getCurrentChar(editorObj)
            if c in editorObj.punctuationChars:
                moveForward = False
                break
            if editorObj.currentLineIndex == 0:
                moveForward = False
                break
            if editorObj.currentLineIndex < 0:
                editorObj.currentLineIndex = 0
                break

        if moveForward:
            editorMovement.moveRight(editorObj)

def jump_to_line(editorObj, repeats):
    """
    Jump to the beginning of the line, and then from the beginning
    walk down to the line number equivalent to repeats.
    """
    editorObj.topLine = editorObj.lineLinkedList.start
    editorObj.topLineCount = 1
    y = 0
    editorObj.currentLineIndex = 0

    for i in range(repeats-1):
        if editorObj.topLine.nextNode is None:
            break
        editorObj.topLine = editorObj.topLine.nextNode
        editorObj.topLineCount += 1

    editorObj.currentLine = editorObj.topLine
