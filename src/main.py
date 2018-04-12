import string  # ascii, digits lists
import os  # for file subsystem (os.chdir, os.getcwd, etc)
import sys  # for sys.exit
# as asynchronously as gil (global interpreter lock) will let me

import curses  # drawing the editor

from dataStructures.lineLinkedList import LineLinkedList
from dataStructures.undoRedoStack import UndoRedoStack
from dataStructures.bkTree import bk_tree
from Util.initCurses import initColors, initScreens
from constants import State, WindowConstants

import Util.fileUtil as fileUtil
import Util.editorUtil as editorUtil
import Util.cursesUtil as cursesUtil
import Util.drawUtil as drawUtil
import Util.syntaxHighlighting as syntaxHighlighting
import Util.changeColorsUtil as changeColorsUtil

from algorithms.binSearch import dirBinSearch
import algorithms.kmp as kmp

import movement.fileNavMovement as fileNavMovement
import movement.editorMovement as editorMovement
import movement.editorJumps as editorJumps


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
        self.fileName = ''
        self.lineLinkedList = LineLinkedList(['\n'])

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

        # draw everything for first iteration
        syntaxHighlighting.setColors(self, self.colorMap)
        drawUtil.drawLineNumbers(self)
        drawUtil.drawLines(self, self.editorscr, self.topLine)
        self.setState(State.NORMAL)
        self.commandRepeats = ''

        # set up punctuation dictionary for fast checking of punctuation
        self.punctuationChars = {}
        for c in string.punctuation:
            self.punctuationChars[c] = True

        # set up bk tree for spellcheck
        self.spellCheckLine = 1000
        spellCheckStream = open('dataStructures/words.txt')
        self.spellCheckWords = []
        for line in spellCheckStream:
            self.spellCheckWords.append(line[:-1])  # take off newline character
        self.spellCheck = bk_tree()

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
        drawUtil.drawLines(self, self.filenavscr, self.topDir)

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
                    drawUtil.drawLines(self, self.editorscr, self.topLine)
                    drawUtil.drawLineNumbers(self)

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
        if self.spellCheckLine < 9998:
            self.spellCheckLine += 1
            self.spellCheck.add(self.spellCheckWords[self.spellCheckLine])

        while True:

            # set everything up for the run
            (y, x) = self.editorscr.getyx()  # get cursor position relative to top left
            repeats = 1 if self.commandRepeats == '' else int(self.commandRepeats)

            if self.state == State.NORMAL:
                c = chr(self.editorscr.getch())  # get a key

                # movement
                # remember top left is (0, 0)
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
                    editorJumps.jump_forward_one_word(self, repeats, x)

                elif c == 'e':
                    editorJumps.jump_one_word_and_whitespace(self, repeats, x)

                elif c == 'b':
                    editorJumps.jump_backward_one_word(self, repeats, x)

                elif c == 'g':
                    editorJumps.jump_to_line(self, repeats)

                elif c == '/':  # search function
                    pattern_to_find = editorUtil.getCmd(self, altDisplayChar='/')
                    self.matchBuffer = (editorUtil.find_pattern_in_syntax(
                                                            self, pattern_to_find))
                    self.currentLine = self.topLine = self.lineLinkedList.start
                    # go to first match
                    if self.matchBuffer:
                        (lineNumber, lineIndex) = self.matchBuffer[0]
                        editorUtil.move_to_node_and_index(self, lineNumber, lineIndex)
                        temp = self.matchBuffer[0]
                        del self.matchBuffer[0]
                        self.matchBuffer.append(temp)


                elif c == 'n':
                    # jump to the next thing in the match buffer
                    if self.matchBuffer != []:
                        (lineNumber, lineIndex) = self.matchBuffer[0]
                        editorUtil.move_to_node_and_index(self, lineNumber, lineIndex)
                        temp = self.matchBuffer[0]
                        del self.matchBuffer[0]
                        self.matchBuffer.append(temp)

                # move to different states
                elif c == 'd':
                    if self.deleteMode is True:  # equivalent to dd command
                        self.undoRedoStack.pushOntoUndo(self)
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
                    self.undoRedoStack.undo(self)

                elif c == chr(18):  # ctrl + r
                    self.undoRedoStack.redo(self)

                elif c in [str(x) for x in range(10)]:
                    self.commandRepeats += str(c)
                    continue

                elif c == 'i':
                    self.undoRedoStack.pushOntoUndo(self)
                    # put currentLine and its value onto undo stack
                    self.setState(State.INSERT)

                elif c == 'a':
                    self.undoRedoStack.pushOntoUndo(self)
                    # put currentLine and its value onto undo stack
                    if editorUtil.getCurrentChar(self) == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                    if editorUtil.getNextChar(self) == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    editorMovement.moveRight(self)
                    self.setState(State.APPEND)

                elif c == 'A':
                    editorUtil.moveToEndOfLine(self)
                    self.undoRedoStack.pushOntoUndo(self)
                    if editorUtil.getNextChar(self) == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    editorMovement.moveRight(self)
                    self.setState(State.APPEND)

                elif c == 'x':
                    # delete character
                    editorUtil.deleteCharacter(self, self.currentLine, self.currentLineIndex)

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

            drawUtil.drawLines(self, self.editorscr, self.topLine)
            drawUtil.drawLineNumbers(self)

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

                else:  # any other character
                    #editorUtil.insert_character(self.currentLine, self.currentLineIndex, c)
                    self.currentLine.value = (self.currentLine.value[:self.currentLineIndex] +
                            c + self.currentLine.value[self.currentLineIndex:])
                    self.currentLineIndex += 1
                    self.currentLine.colors.append(0)

            elif self.state == State.VISUAL:
                cursesUtil.kill(self)
                raise NotImplementedError

            elif self.state == State.COMMAND_LINE:

                cmd_string = editorUtil.getCmd(self)

                if cmd_string == chr(27):  # escape character
                    self.setState(State.NORMAL)
                    continue
                cmd_list = cmd_string.strip(' \t\n\r')
                # tokenize based on '|'
                cmds = cmd_list.split('|')
                for cmd in cmds:
                    for cmdChar in cmd:
                        if cmdChar == 'w':
                            args = cmd.split()
                            # what if the fileName is ''?
                            if self.fileName is '':
                                if len(args) - 1 > 0:
                                    self.fileName = args[1]
                                    fileUtil.saveFile(self)
                                    self.drawAndRefreshFileNavigation()
                                    # disp new file if one is made
                                else:
                                    self.statusscr.clear()
                                    self.statusscr.addstr('Error; No file name')
                                    self.statusscr.refresh()
                            else:
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
                            cursesUtil.kill(self)
                            drawUtil.drawTerminalChatter(self, cmd)

                            # bring what we killed back to life
                            cursesUtil.birth()

                # set state to normal upon exit
                self.setState(State.NORMAL)

            elif self.state == State.FILE_NAVIGATION:
                self.runFileNavigation()

            elif self.state == State.OPTIONS:
                self.editorscr.clear()

                # save all of the pointers for later
                tempLinkedList = self.lineLinkedList
                tempCurrentLine = self.currentLine
                tempTopLine = self.topLine

                optionsText = LineLinkedList(['Change Colors'])
                self.lineLinkedList = optionsText
                self.topLine = self.currentLine = self.lineLinkedList.start

                drawUtil.drawLineNumbers(self)
                drawUtil.drawLines(self, self.editorscr, self.topLine)
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

            # draw everything again
            syntaxHighlighting.setColors(self, self.colorMap)
            drawUtil.drawStatus(self)  # draw the status bar text on status bar
            drawUtil.drawLines(self, self.editorscr, self.topLine)
            drawUtil.drawLineNumbers(self)


if __name__ == "__main__":
    editor = MainScr()
    editor.run()
