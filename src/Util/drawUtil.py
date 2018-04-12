from dataStructures.lineLinkedList import LineLinkedList

import Util.editorUtil as editorUtil

import subprocess  # need it for drawTerminalChatter
import os  # need it for drawStatus
import curses  # need it for drawLines

def drawTerminalChatter(editorObj, cmd):
    """
    Output whatever process sends to stdout in real time
    """
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

    # clean the screen to prepare for output
    editorObj.editorscr.clear()

    # save these for later
    tempLinkedList = editorObj.lineLinkedList
    tempPointer = editorObj.topLine

    outputStr = ''

    while True:
        out = process.stdout.read(1).decode()
        if out == '' and process.poll() is not None:
            break
        if out != '':
            outputStr += out
            consoleChatterLines = LineLinkedList(outputStr.split('\n'))

            # set these so you can use drawLines
            editorObj.lineLinkedList = consoleChatterLines
            editorObj.topLine = editorObj.lineLinkedList.start

            # draw the output
            drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
            editorObj.drawLineNumbers()
            editorObj.editorscr.refresh()
    # kill the pipe
    process.stdout.close()

    # now wait for the user to send some ready confirmation
    # that he's seen the output and he's good to go
    editorObj.statusscr.clear()
    editorObj.statusscr.addstr('Please press any key to proceed.')
    editorObj.statusscr.refresh()

    editorObj.editorscr.getch()  # wait for confirmation

    # set the old lines and topline back
    editorObj.lineLinkedList = tempLinkedList
    editorObj.topLine = tempPointer

    drawLines(editorObj, editorObj.editorscr, editorObj.topLine)
    editorObj.drawLineNumbers()
    editorObj.editorscr.refresh()

def drawStatus(editorObj):
    """
    Draws status using whatever is set as default
    """
    editorObj.statusscr.clear()
    checkStr = (editorObj.getStateStr() + '  ' + os.getcwd() +
                        '/' + editorObj.fileName + '  ' + 'Line ' +
                        str(editorObj.currentLineCount) +
                        ' Column ' + str(editorObj.currentLineIndex))
    if len(checkStr) > editorObj.statusscr.getmaxyx()[1]:
        checkStr = checkStr[:editorObj.statusscr.getmaxyx()[1]-2]
    editorObj.statusscr.addstr(checkStr)
    editorObj.statusscr.refresh()

def drawLineNumbers(editorObj):
    """
    Draws the line numbers on editorscr, using the corresponding linenumscr.
    Only relevant for use by linenumscr.
    """
    # clear old data off the screen
    editorObj.linenumscr.clear()

    (moveY, moveX) = (0, 0)

    # draw line numbers
    lineToDraw = editorObj.topLine
    y = 0
    lineIndex = editorObj.topLineCount
    editorObj.linenumscr.move(0, 0)
    while y < editorObj.linenumscr.getmaxyx()[0]-1:
        editorObj.linenumscr.addstr(str(lineIndex))

        if lineToDraw == editorObj.currentLine:
            moveY = y + editorObj.currentLineIndex//editorObj.editorscr.getmaxyx()[1]
            for i in range(editorObj.currentLineIndex):
                c = editorObj.currentLine.value[i]
                if c == '\t':
                    moveX += 8
                else:
                    moveX += 1
                if moveX > editorObj.editorscr.getmaxyx()[1]:
                    moveX -= editorObj.editorscr.getmaxyx()[1]
                moveX = moveX % editorObj.editorscr.getmaxyx()[1]

            editorObj.currentLineCount = lineIndex
            if moveX <= -1:
                moveX = 0

        y += editorUtil.lineHeight(editorObj.editorscr, lineToDraw)

        if lineToDraw.nextNode is None:  # ran out of nodes
            break
        lineToDraw = lineToDraw.nextNode
        lineIndex += 1

        if y > editorObj.linenumscr.getmaxyx()[0]-1:
            break
        editorObj.linenumscr.move(y, 0)

    editorObj.editorscr.move(moveY, moveX)

def drawLines(editorObj, scr, topLine):
    """
    Takes in a scr object from which it draws on

    Draws the line numbers and the lines themselves onto the ui
    O(n) where n is the number of blocks that can fit onto the terminal,
    but since n is very small and theta(n) is a fraction of
    n usually < n/2 this is fine.
    """
    # clear the old data off of the screen
    scr.clear()

    # draw the lines themselves
    lineToDraw = topLine
    scr.move(0, 0)
    cursorY = 0

    while lineToDraw is not None:

        if scr.getyx()[0] + editorUtil.lineHeight(editorObj.editorscr, lineToDraw) > scr.getmaxyx()[0]-1:
            # handle no space at bottom when scrolling up
            scr.addstr('@')
            break
        i = 0
        for c in lineToDraw.value:
            colorToDraw = lineToDraw.colors[i]
            scr.addstr(c, curses.color_pair(colorToDraw))
            currentX = scr.getyx()[1]
            if currentX+1 > scr.getmaxyx()[1]-1:
                # if we have reached the end of the line horizontally
                cursorY += 1
                scr.move(cursorY, 0)
            i += 1

        if scr.getyx()[0] + 1 > scr.getmaxyx()[0]-1:
            break
        scr.move(cursorY + 1, 0)
        cursorY += 1
        lineToDraw = lineToDraw.nextNode

    # move cursor to where it should be as
    # specified by currentLine and currentLineIndex, refresh and move on
    editorObj.linenumscr.refresh()
    scr.refresh()

