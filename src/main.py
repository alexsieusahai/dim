import string  # ascii, digits lists
import os  # for file subsystem (os.chdir, os.getcwd, etc)
import sys  # for sys.exit
import subprocess  # for BANG!

import curses  # drawing the editor

from dataStructures.lineLinkedList import LineLinkedList
from dataStructures.undoRedoStack import UndoRedoStack
from Util.initCurses import initColors, initScreens
from constants import State, WindowConstants
import Util.fileUtil as fileUtil
import Util.editorUtil as editorUtil
import Util.cursesUtil as cursesUtil
import Util.syntaxHighlighting as syntaxHighlighting
import Util.changeColorsUtil as changeColorsUtil
from algorithms.binSearch import dirBinSearch
import algorithms.kmp as kmp
import movement.fileNavMovement as fileNavMovement
import movement.editorMovement as editorMovement


class MainScr:

    def __init__(self):
        """
        Inits screens, curses stuff, colors, attributes, etc
        """
        # set up curses stuff
        initScreens(self, WindowConstants)
        cursesUtil.birth()

        # init all the colors
        self.dimDir = os.getcwd()
        self.colorMap = initColors(self.dimDir, 'default.json')
        self.stdscr.attrset(curses.color_pair(self.colorMap['TEXT']))
        self.stdscr.bkgd(' ', curses.color_pair(self.colorMap['TEXT']))
        self.editorscr.bkgd(' ', curses.color_pair(self.colorMap['TEXT']))
        self.filenavscr.bkgd(' ', curses.color_pair(self.colorMap['TEXT']))
        self.filenavscr.refresh()
        self.linenumscr.attrset(
                curses.color_pair(self.colorMap['LINE_NUMBER'])
                )
        self.linenumscr.bkgd(
                ' ', curses.color_pair(self.colorMap['LINE_NUMBER'])
                )
        self.cmdlinescr.attrset(
                curses.color_pair(self.colorMap['TEXT'])
                )
        self.cmdlinescr.bkgd(
                ' ', curses.color_pair(self.colorMap['TEXT'])
                )

        self.setState(State.NORMAL)
        self.runFileNavigation(breakEarly=True)
        self.matchBuffer = []

        # grabbing the lines from the file
        self.fileName = 'test.py'
        self.lineLinkedList = fileUtil.loadFile(self.fileName)

        # make and store the savefile here

        (maxY, maxX) = self.stdscr.getmaxyx()

        # setting ui up
        self.editorscr.move(0, 0)
        self.currentLineCount = 0

        # set up something bright for statusscr
        self.statusscr.bkgd(' ', curses.color_pair(self.colorMap['STATUS']))
        self.statusscr.attrset(curses.color_pair(self.colorMap['STATUS']))
        self.statusscr.refresh()

        # keep 2 pointers; 1 for top line node, 1 for current line node
        self.topLine = self.currentLine = self.lineLinkedList.start
        self.topLineCount = 1  # number to draw for topLine
        self.currentLineIndex = 0

        # set up undo redo stack
        self.undoRedoStack = UndoRedoStack()

        self.drawLines(self.editorscr, self.topLine)
        self.drawLineNumbers()
        self.setState(State.NORMAL)
        self.commandRepeats = ''

        # set up punctuation dictionary for fast checking of punctuation
        self.punctuationChars = {}
        for c in string.punctuation:
            self.punctuationChars[c] = True

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Prepares curses and filesystem for exit
        """
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()

    def setState(self, stateToSet):
        try:
            if self.state is State.NORMAL and stateToSet is State.APPEND:
                self.appendLineNode = self.currentLine
        except AttributeError:
            self.state = stateToSet
        if self.state is State.APPEND:
            if len(self.appendLineNode.value) > 1:
                if self.appendLineNode.value[-2] == ' ':
                    self.appendLineNode.value = self.appendLineNode.value[:-2]+'\n'
        self.state = stateToSet

    def getStateStr(self):
        if self.state is State.NORMAL:
            return 'NORMAL'
        elif self.state is State.INSERT:
            return 'INSERT'
        elif self.state is State.VISUAL:
            return 'VISUAL'
        elif self.state is State.COMMAND_LINE:
            return 'CMD_LINE'
        elif self.state is State.FILE_NAVIGATION:
            return 'FILE_NAV'
        elif self.state is State.APPEND:
            return 'APPEND'
        else:
            return 'UNKNOWN_STATE'

    def getState(self):
        return self.state

    def moveToNode(self, line, lineIndex):
        self.currentLine = self.topLine = self.lineLinkedList.start
        while self.currentLine != line:
            editorMovement.moveDown(self)
        self.currentLineIndex = lineIndex
        pass

    def moveToIndex(self, lineNumber, lineIndex):
        self.currentLine = self.topLine = self.lineLinkedList.start
        for i in range(lineNumber-1):
            editorMovement.moveDown(self)
        self.currentLineIndex = lineIndex

    def drawLineNumbers(self):

        # clear old data off the screen
        self.linenumscr.clear()

        (moveY, moveX) = (0, 0)

        # draw line numbers
        lineToDraw = self.topLine
        if self.topLine is None:
            assert(False)
        y = 0
        lineIndex = self.topLineCount
        self.linenumscr.move(0, 0)
        while y < self.linenumscr.getmaxyx()[0]-1:
            self.linenumscr.addstr(str(lineIndex))

            if lineToDraw == self.currentLine:
                moveY = y + self.currentLineIndex//self.editorscr.getmaxyx()[1]
                # below solution doesn't work for tabs, but way faster
                #moveX = min(
                #        self.currentLineIndex % self.editorscr.getmaxyx()[1],
                #        len(self.currentLine.value)-2
                #        )  # avoid the newline char
                for i in range(self.currentLineIndex):
                    c = self.currentLine.value[i]
                    if c == '\t':
                        moveX += 8
                    else:
                        moveX += 1
                    if moveX > self.editorscr.getmaxyx()[1]:
                        moveX -= self.editorscr.getmaxyx()[1]
                    moveX = moveX % self.editorscr.getmaxyx()[1]

                self.currentLineCount = lineIndex
                if moveX <= -1:
                    moveX = 0

            y += editorUtil.lineHeight(self.editorscr, lineToDraw)

            if lineToDraw.nextNode is None:  # ran out of nodes
                break
            lineToDraw = lineToDraw.nextNode
            lineIndex += 1

            if y > self.linenumscr.getmaxyx()[0]-1:
                break
            self.linenumscr.move(y, 0)

        self.editorscr.move(moveY, moveX)

    def drawLines(self, scr, topLine):
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

            if scr.getyx()[0] + editorUtil.lineHeight(self.editorscr, lineToDraw) > scr.getmaxyx()[0]-1:
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
        self.linenumscr.refresh()
        scr.refresh()

    def drawStatus(self):
        """
        Draws status using whatever is set as default
        """
        self.statusscr.clear()
        checkStr = (self.getStateStr() + '  ' + os.getcwd() +
                    '/' + self.fileName + '  ' + 'Line ' +
                    str(self.currentLineCount) +
                    ' Column ' + str(self.currentLineIndex))
        if len(checkStr) > self.statusscr.getmaxyx()[1]:
            checkStr = checkStr[:self.statusscr.getmaxyx()[1]-2]
        self.statusscr.addstr(checkStr)
        self.statusscr.refresh()

    def outputTerminalChatter(self, process):
        """
        Output whatever process sends to stdout in real time
        """

        # clean the screen to prepare for output
        self.editorscr.clear()

        # save these for later
        tempLinkedList = self.lineLinkedList
        tempPointer = self.topLine

        outputStr = ''

        while True:

            out = process.stdout.read(1).decode()
            if out == '' and process.poll() is not None:
                break
            if out == '':
                outputStr = process.poll()
            if out != '':
                outputStr += out
                consoleChatterLines = LineLinkedList(outputStr.split('\n'))

                # set these so you can use drawLines
                self.lineLinkedList = consoleChatterLines
                self.topLine = self.lineLinkedList.start

                # draw the output
                self.drawLines(self.editorscr, self.topLine)
                self.drawLineNumbers()
                self.editorscr.refresh()

        # kill the pipe
        process.stdout.close()

        # now wait for the user to send some ready
        # confirmation that he's seen the output and he's good to go
        self.statusscr.clear()
        self.statusscr.addstr('Please press any key to proceed.')
        self.statusscr.refresh()

        self.editorscr.getch()  # wait for confirmation

        # set the old lines and topline back
        self.lineLinkedList = tempLinkedList
        self.topLine = tempPointer

        self.drawLines(self.editorscr, self.topLine)
        self.drawLineNumbers()
        self.editorscr.refresh()

    def setUpFileHighlighting(self):
        directory = self.dirs.start
        while directory is not None:
            color = self.colorMap['FILE']
            if os.path.isdir(directory.value):
                color = self.colorMap['FOLDER']
            for i in range(len(directory.value)):
                directory.colors[i] = color
            directory = directory.nextNode

    def drawAndRefreshFileNavigation(self):

        self.filenavscr.clear()
        self.drawLines(self.filenavscr, self.topDir)

    def runFileNavigation(self, breakEarly=False):

        self.dirs = LineLinkedList(editorUtil.getDirs())
        self.topDir = self.currentDir = self.dirs.start
        self.setUpFileHighlighting()
        self.drawAndRefreshFileNavigation()
        self.filenavscr.move(0, 0)

        y = 0

        while True:

            if breakEarly:
                self.setState(State.NORMAL)
                break

            c = chr(self.filenavscr.getch())

            if c == '`':
                self.setState(State.NORMAL)
                break

            if c == 'k':
                y = fileNavMovement.moveUp(self, y)

            elif c == 'j':
                y = fileNavMovement.moveDown(self, y)

            elif c == '\n':
                try:
                    os.chdir(self.currentDir.value)
                    self.dirs = LineLinkedList(editorUtil.getDirs())
                    self.currentDir = self.topDir = self.dirs.start
                    self.setUpFileHighlighting()

                except NotADirectoryError:
                    # reload file and prep
                    self.fileName = self.currentDir.value
                    self.lineLinkedList = fileUtil.loadFile(self.fileName)
                    self.topLine = self.currentLine = self.lineLinkedList.start
                    self.currentLineIndex = 0
                    syntaxHighlighting.setColors(self, self.colorMap)
                    self.drawLines(self.editorscr, self.topLine)
                    self.drawLineNumbers()

                    # reset file dir
                    self.currentDir = self.topDir = self.dirs.start
                y = 0

            elif c == '?':
                searchSubStr = editorUtil.getCmd(self, altDisplayChar='?')[1:]
                # want to take off the '?' character from the start
                searchSubStr = searchSubStr.lstrip()
                if searchSubStr == chr(27):  # escape character
                    continue
                else:
                    wantedDir = dirBinSearch(self.dirs, self.dirs.toList(),
                                        searchSubStr, self.currentDir)
                    if wantedDir is None:  # we couldn't find anything
                        continue

                    y = 0
                    self.currentDir = self.topDir = self.dirs.start
                    while self.currentDir != wantedDir:
                        y = fileNavMovement.moveDown(self, y)

            self.drawAndRefreshFileNavigation()
            self.filenavscr.move(y, 0)

    def run(self):
        """
        Main loop of the state machine
        """
        while True:

            # set everything up for the run
            syntaxHighlighting.setColors(self, self.colorMap)
            self.drawStatus()  # draw the status bar text on status bar
            self.drawLines(self.editorscr, self.topLine)
            self.drawLineNumbers()
            (y, x) = self.editorscr.getyx()  # get cursor position relative to top left
            repeats = 1 if self.commandRepeats == '' else int(self.commandRepeats)

            if self.state == State.NORMAL:
                c = chr(self.editorscr.getch())  # get a key

                # movement
                # remember top left is (0,0)
                if c == 'j':  # down
                    editorMovement.moveDown(self)
                elif c == 'k':  # up
                    editorMovement.moveUp(self)
                elif c == 'h':  # left
                    editorMovement.moveLeft(self)
                elif c == 'l':  # right
                    editorMovement.moveRight(self)
                elif c == '$':  # eol
                    editorUtil.moveToEndOfLine(self)
                elif c == '0':  # beginning
                    if self.commandRepeats != '':
                        self.commandRepeats += '0'
                        continue
                    editorUtil.moveToBeginningOfLine(self)

                elif c == 'w':
                    """
                    Walk through elements on line until you hit
                    either punctuation (where you stop) or spaces
                    (where you walk through until you hit something that isn't a space)
                    """
                    for i in range(repeats):

                        # handle edge case of `w` on '\n' line
                        if editorUtil.getCurrentChar(self) == '\n':
                            if self.deleteMode is True:
                                editorUtil.deleteCharacter(self, self.currentLine, x)
                                self.drawLineNumbers()
                            else:
                                editorMovement.moveDown(self)
                                self.currentLineIndex = 0
                            continue

                        if editorUtil.getNextChar(self) == '\n':
                            if self.deleteMode is True:
                                editorUtil.deleteCharacter(self, self.currentLine, x)
                            else:
                                editorMovement.moveDown(self)
                                self.currentLineIndex = 0
                            continue

                        while True:

                            if self.deleteMode is True:
                                editorUtil.deleteCharacter(self, self.currentLine, x)
                            else:
                                editorMovement.moveRight(self)
                            self.drawLines(self.editorscr, self.topLine)
                            self.drawLineNumbers()
                            c = editorUtil.getCurrentChar(self)

                            if c in self.punctuationChars:
                                break

                            if editorUtil.getNextChar(self) == '\n':
                                if self.deleteMode is True:
                                    editorUtil.deleteCharacter(self, self.currentLine, x)
                                    editorUtil.deleteCharacter(self, self.currentLine, x)
                                else:
                                    editorMovement.moveDown(self)
                                    self.currentLineIndex = 0
                                self.drawLines(self.editorscr, self.topLine)
                                self.drawLineNumbers()
                                break

                            if c == ' ':
                                while c == ' ':
                                    if self.deleteMode is True:
                                        editorUtil.deleteCharacter(self, self.currentLine, x)
                                    else:
                                        editorMovement.moveRight(self)
                                    self.drawLines(self.editorscr, self.topLine)
                                    self.drawLineNumbers()
                                    c = editorUtil.getCurrentChar(self)
                                    if editorUtil.getNextChar(self) == '\n':
                                        break
                                break

                elif c == 'e':

                    for i in range(repeats):
                        # handle edge case of `e` on '\n' line
                        if self.currentLine.value == '\n' or editorUtil.getNextChar(self) == '\n':
                            if self.deleteMode is True:
                                if self.currentLine.value == '\n':
                                    editorUtil.deleteCharacter(self, self.currentLine, x)
                                else:
                                    editorUtil.deleteCharacter(self, self.currentLine, x)
                                    editorUtil.deleteCharacter(self, self.currentLine, x)
                                continue

                            editorMovement.moveDown(self)
                            self.currentLineIndex = 0
                            continue

                        if self.deleteMode is True:
                            editorUtil.deleteCharacter(self, self.currentLine, x)
                        else:
                            editorMovement.moveRight(self)

                        while True:
                            while (editorUtil.getNextChar(self) == ' ' or
                                    editorUtil.getNextChar(self) in string.ascii_letters):
                                if self.deleteMode is True:
                                    editorUtil.deleteCharacter(self, self.currentLine, x)
                                else:
                                    editorMovement.moveRight(self)
                            self.drawLines(self.editorscr, self.topLine)
                            self.drawLineNumbers()
                            break

                        if self.deleteMode is True:
                            editorUtil.deleteCharacter(self, self.currentLine, x)

                elif c == 'b':
                    """
                    Walk through elements on the line _backwards_
                    until the character before is punctuation or a space
                    """

                    for i in range(repeats):

                        moveForward = True
                        editorMovement.moveLeft(self)
                        self.currentLineIndex -= 1
                        if self.currentLineIndex < 0:
                            if self.currentLine.lastNode is None:
                                self.currentLineIndex = 0
                                continue
                            editorMovement.moveUp(self)
                            editorUtil.moveToEndOfLine(self)
                            self.drawLines(self.editorscr, self.topLine)
                            self.drawLineNumbers()
                            self.currentLineIndex = 0

                        if len(self.currentLine.value) <= 2:
                            continue

                        # now we are guaranteed a line
                        # with at least two characters
                        c = editorUtil.getCurrentChar(self)

                        while c == ' ':
                            editorMovement.moveLeft(self)
                            self.drawLines(self.editorscr, self.topLine)
                            self.drawLineNumbers()
                            c = editorUtil.getCurrentChar(self)
                            if c in self.punctuationChars:
                                moveForward = False
                                break
                            if self.editorscr.getyx()[1] == 0:
                                if self.currentLine == 0:
                                    moveForward = False
                                    break
                                editorMovement.moveUp(self)
                                self.drawLines(self.editorscr, self.topLine)
                                self.drawLineNumbers()
                                editorUtil.moveToEndOfLine(self)
                                self.drawLines(self.editorscr, self.topLine)
                                self.drawLineNumbers()

                        while c in string.ascii_letters or c in string.digits:
                            editorMovement.moveLeft(self)
                            self.drawLines(self.editorscr, self.topLine)
                            self.drawLineNumbers()
                            c = editorUtil.getCurrentChar(self)
                            if c in self.punctuationChars:
                                moveForward = False
                                break
                            if self.currentLineIndex == 0:
                                moveForward = False
                                break
                            if self.currentLineIndex < 0:
                                self.currentLineIndex = 0
                                break

                        if moveForward:
                            editorMovement.moveRight(self)
                            self.drawLines(self.editorscr, self.topLine)
                            self.drawLineNumbers()

                elif c == 'g':  # go to beginning of file
                    self.currentLine = self.topLine = self.lineLinkedList.start
                    for i in range(repeats-1):
                        editorMovement.moveDown(self)

                elif c == '/':  # search function
                    patternToFind = editorUtil.getCmd(self, altDisplayChar='/')
                    if patternToFind[0] == '/':
                        patternToFind = patternToFind[1:]
                    walk = self.lineLinkedList.start
                    self.matchBuffer = []
                    lineNumber = 1
                    while walk is not None:
                        matches = kmp.kmp(walk.value, patternToFind)
                        if matches:
                            for match in matches:
                                self.matchBuffer.append((lineNumber, match))
                        walk = walk.nextNode
                        lineNumber += 1
                    self.currentLine = self.topLine = self.lineLinkedList.start
                    # go to first match
                    if self.matchBuffer:
                        (lineNumber, lineIndex) = self.matchBuffer[0]
                        self.moveToIndex(lineNumber, lineIndex)
                        temp = self.matchBuffer[0]
                        del self.matchBuffer[0]
                        self.matchBuffer.append(temp)

                elif c == 'n':
                    # jump to the next thing in the match buffer
                    if self.matchBuffer != []:
                        (lineNumber, lineIndex) = self.matchBuffer[0]
                        self.moveTo(lineNumber, lineIndex)
                        temp = self.matchBuffer[0]
                        del self.matchBuffer[0]
                        self.matchBuffer.append(temp)

                # move to different states
                elif c == 'd':
                    if self.deleteMode is True:  # equivalent to dd command
                        if self.currentLine.nextNode is None: # last node
                            temp = self.currentLine.lastNode
                            editorUtil.deleteLine(self, self.currentLine, trueDelete=True)
                            self.currentLine = temp
                        else:
                            self.currentLine = editorUtil.deleteLine(self, self.currentLine,
                                                                        trueDelete=True)
                        self.deleteMode = False
                    else:
                        self.deleteMode = True
                    continue

                elif c == 'u':  # undo
                    #self.undoRedoStack.undo(self)
                    raise NotImplementedError

                elif c == chr(18):  # ctrl + r
                    #self.undoRedoStack.redo(self)
                    raise NotImplementedError

                elif c in [str(x) for x in range(10)]:
                    self.commandRepeats += str(c)
                    continue

                elif c == 'i':
                    self.setState(State.INSERT)

                elif c == 'a':
                    if editorUtil.getNextChar(self) == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    editorMovement.moveRight(self)
                    self.drawLines(self.editorscr, self.topLine)
                    self.drawLineNumbers()
                    self.setState(State.APPEND)

                elif c == 'A':
                    editorUtil.moveToEndOfLine(self)
                    if editorUtil.getNextChar(self) == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    editorMovement.moveRight(self)
                    self.drawLines(self.editorscr, self.topLine)
                    self.drawLineNumbers()
                    self.setState(State.APPEND)

                elif c == 'x':
                    # delete character
                    editorUtil.deleteCharacter(self, self.currentLine, self.currentLineIndex)
                    self.drawLines(self.editorscr, self.topLine)
                    self.drawLineNumbers()

                elif c == 'v':
                    self.setState(State.VISUAL)

                elif c == ':':
                    self.setState(State.COMMAND_LINE)

                elif c == '`':
                    self.setState(State.FILE_NAVIGATION)

                elif c == '.':
                    self.setState(State.OPTIONS)

                self.deleteMode = False
                self.commandRepeats = ''


            if self.state == State.INSERT or self.state == State.APPEND:

                c = chr(self.editorscr.getch())

                if ord(c) == 27:  # escape
                    editorMovement.moveLeft(self)
                    self.setState(State.NORMAL)

                elif ord(c) == 127:  # backspace
                    self.currentLine.value = (self.currentLine.value[:max(self.
                            currentLineIndex-1, 0)]+self.currentLine.value[max(self
                                                            .currentLineIndex, 0):])
                    self.currentLineIndex -= 1
                    self.colors = self.currentLine.colors[:-1]

                    if self.currentLineIndex == -1:
                        # delete the line
                        self.currentLine = editorUtil.deleteLine(self, self.currentLine)

                elif ord(c) == 10:   # enter

                    # keeping for undo
                    undoValue = self.currentLine.value

                    if self.editorscr.getyx()[0] + 1 > self.editorscr.getmaxyx()[0] -2:
                        self.topLine = self.topLine.nextNode
                    self.currentLine = editorUtil.insertLine(self, self.currentLine)
                    editorUtil.moveToBeginningOfLine(self)
                    # get the spacing from the line above
                    i = 0
                    lastLineValue = self.currentLine.lastNode.value
                    while True:
                        if lastLineValue[i] == ' ' or lastLineValue[i] == '\t':
                            self.currentLine.value = (self.currentLine.value[:-1]+
                            ('\t' if lastLineValue[i] == '\t' else ' ')+'\n')
                            self.currentLineIndex += 1
                            self.currentLine.colors.append(0)
                            i += 1
                        else:
                            break

                    self.drawLines(self.editorscr, self.topLine)
                    self.drawLineNumbers()

                else:  # any other character
                    self.currentLine.value = (self.currentLine.value[:self.currentLineIndex] +
                            c + self.currentLine.value[self.currentLineIndex:])
                    self.currentLineIndex += 1
                    self.currentLine.colors.append(0)
                    self.drawLines(self.editorscr, self.topLine)
                    self.drawLineNumbers()

            elif self.state == State.VISUAL:
                cursesUtil.kill(self)
                raise NotImplementedError

            elif self.state == State.COMMAND_LINE:
                # what about if user presses escape?
                cmd = editorUtil.getCmd(self)

                if cmd == chr(27):  # escape character
                    self.setState(State.NORMAL)
                    continue
                cmd = cmd.strip(' \t\n\r')
                # tokenize based on '|'
                cmds = cmd.split('|')
                for cmd in cmds:
                    for cmdChar in cmd:
                        if cmdChar == 'w':
                            fileUtil.saveFile(self)
                        if cmdChar == 'q':
                            cursesUtil.kill(self)
                            sys.exit(0)
                        if cmdChar == '!':
                            # clear the screens to prep
                            self.stdscr.clear()
                            self.editorscr.clear()
                            self.linenumscr.clear()

                            # kill the process to give stdin pipe back to terminal
                            cursesUtil.kill(self)

                            if cmd[0] == ':':
                                cmd = cmd[1:]
                            if cmd[0] == '!':
                                cmd = cmd[1:]

                            process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

                            self.outputTerminalChatter(process)

                            # bring what we killed back to life
                            cursesUtil.birth()

                # set state to normal upon exit
                self.setState(State.NORMAL)

            elif self.state == State.FILE_NAVIGATION:
                self.runFileNavigation()

            elif self.state == State.OPTIONS:
                self.editorscr.clear()
                optionsText = LineLinkedList(['Change Colors'
                                                            ])

                # save all of the pointers for later
                tempLinkedList = self.lineLinkedList
                tempCurrentLine = self.currentLine
                tempTopLine = self.topLine

                self.lineLinkedList = optionsText
                self.topLine = self.currentLine = self.lineLinkedList.start

                self.drawLineNumbers()
                self.drawLines(self.editorscr, self.topLine)
                self.editorscr.refresh()
                self.linenumscr.refresh()

                self.editorscr.move(0,0)

                while True:
                    c = chr(self.editorscr.getch())

                    if c == chr(27):  # escape
                        self.lineLinkedList = tempLinkedList
                        self.topLine = tempTopLine
                        self.currentLine = tempCurrentLine
                        self.state = State.NORMAL
                        break

                    elif c == chr(10):
                        if self.currentLine.value is 'Change Colors':
                            themeFileName = changeColorsUtil.displayThemes(
                                                            self, self.dimDir)
                            # need dimDir so we know the path to themes
                            self.colorMap = initColors(self.dimDir, themeFileName)
                        self.state = State.NORMAL
                        break

                    elif c == 'j':
                        editorMovement.moveDown(self)

                    elif c == 'k':
                        editorMovement.moveUp(self)

                # set everything back to the way it was on the way out
                self.lineLinkedList = tempLinkedList
                self.currentLine = tempCurrentLine
                self.topLine = tempTopLine

if __name__ == "__main__":
    editor = MainScr()
    editor.run()
