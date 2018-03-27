# look into "wrapper" for debugging

from enum import Enum
import string # ascii, digits lists
import os # for file subsystem (os.chdir, os.getcwd, etc)
import sys # for sys.exit
import subprocess # for BANG!
import threading
import time

import curses # drawing the editor
from pygments.lexers import Python3Lexer
import pygments
import shutil # check if something is a executable

from lineLinkedList import LineLinkedList
from lineNode import LineNode

class State(Enum):
    NORMAL = 0
    INSERT = 1
    VISUAL = 2
    COMMAND_LINE = 3
    FILE_NAVIGATION = 4

class NormalState(Enum):
    MOVEMENT = 0
    DELETE = 1
    # what else do I need

class SyntaxColors(Enum):

    # file nav stuff
    FILE = 1
    FOLDER = 2
    EXECUTABLE = 3

    # editor (syntax highlighting) stuff
    TEXT = 20
    CONSTANT = 21
    DECLARATION = 22
    NAMESPACE = 23
    TYPE = 24
    NAME = 25
    FUNCTION = 26
    STRING_LITERAL = 27
    LITERAL = 28
    OPERATOR = 29
    COMMENT = 30
    LINE_NUMBER = 31
    STATUS = 32
    KEYWORD = 33
    BUILTIN = 34

class Colors(Enum):

    MEDIUM_GREY = 10
    WHITE = 11
    COOL_GREY = 12
    BLACK = 13
    YELLOW = 15
    BLUE = 14
    FUCHSIA = 16
    PURPLE = 17
    BROWN = 18
    ORANGE = 19
    LIME_GREEN = 20
    TURQUOISE = 21
    CYAN = 22
    LIGHT_GREY = 23
    PASTEL_RED = 24

MAX_LINE_NUMBER_LENGTH = 4
FILE_SUBSYSTEM_WINDOW_LENGTH = 18

class MainScr:

    def initScreens(self):
        """
        This function initializes all the screens to be painted on
        """
        self.stdscr = curses.initscr()
        self.editorscr = curses.newwin(
                self.stdscr.getmaxyx()[0]-2,
                self.stdscr.getmaxyx()[1]-(MAX_LINE_NUMBER_LENGTH+1)-FILE_SUBSYSTEM_WINDOW_LENGTH,
                0,
                MAX_LINE_NUMBER_LENGTH+1+FILE_SUBSYSTEM_WINDOW_LENGTH)

        self.linenumscr = curses.newwin(
                self.stdscr.getmaxyx()[0]-2,
                MAX_LINE_NUMBER_LENGTH+1,
                0,
                FILE_SUBSYSTEM_WINDOW_LENGTH)

        self.filenavscr = curses.newwin(
                self.stdscr.getmaxyx()[0],
                FILE_SUBSYSTEM_WINDOW_LENGTH,
                0,
                0)

        self.statusscr = curses.newwin(
                1,
                self.stdscr.getmaxyx()[1]-FILE_SUBSYSTEM_WINDOW_LENGTH,
                self.stdscr.getmaxyx()[0]-2,
                FILE_SUBSYSTEM_WINDOW_LENGTH)

        self.cmdlinescr = curses.newwin(
                1,
                self.stdscr.getmaxyx()[1]-FILE_SUBSYSTEM_WINDOW_LENGTH,
                self.stdscr.getmaxyx()[0]-1,
                FILE_SUBSYSTEM_WINDOW_LENGTH)

    def initColors(self):
        """
        Initialize all colors and color pairs
        """
        curses.start_color()
        curses.init_color(Colors.COOL_GREY.value, 125, 150, 175)
        curses.init_color(Colors.MEDIUM_GREY.value, 400, 400, 400)
        curses.init_color(Colors.LIGHT_GREY.value, 700, 700, 700)
        curses.init_color(Colors.WHITE.value, 1000, 1000, 1000)
        curses.init_color(Colors.BLACK.value, 0, 0, 0)
        curses.init_color(Colors.YELLOW.value, 1000, 1000, 0)
        curses.init_color(Colors.BLUE.value, 0, 0, 1000)
        curses.init_color(Colors.FUCHSIA.value, 1000, 0, 500)
        curses.init_color(Colors.PURPLE.value, 600, 200, 900)
        curses.init_color(Colors.BROWN.value, 750, 200, 70)
        curses.init_color(Colors.ORANGE.value, 1000, 350, 0)
        curses.init_color(Colors.LIME_GREEN.value, 0, 1000, 500)
        curses.init_color(Colors.TURQUOISE.value, 150, 1000, 700)
        curses.init_color(Colors.CYAN.value, 0, 1000, 1000)
        curses.init_color(Colors.PASTEL_RED.value, 1000, 410, 380)

        # handle colors for syntax highlighting
        curses.init_pair(SyntaxColors.TEXT.value, Colors.WHITE.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.LINE_NUMBER.value, Colors.MEDIUM_GREY.value, Colors.COOL_GREY.value) # lighter grey text, cool grey background
        curses.init_pair(SyntaxColors.STATUS.value, Colors.BLACK.value, Colors.WHITE.value)
        curses.init_pair(SyntaxColors.COMMENT.value, Colors.LIGHT_GREY.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.NAMESPACE.value, Colors.LIME_GREEN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.KEYWORD.value, Colors.ORANGE.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.BUILTIN.value, Colors.CYAN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.FUNCTION.value, Colors.LIME_GREEN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.LITERAL.value, Colors.PASTEL_RED.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.OPERATOR.value, Colors.YELLOW.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.STRING_LITERAL.value, Colors.BROWN.value, Colors.COOL_GREY.value)

        # file nav pairs
        curses.init_pair(SyntaxColors.FILE.value, Colors.LIGHT_GREY.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.FOLDER.value, Colors.CYAN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.EXECUTABLE.value, Colors.LIME_GREEN.value, Colors.COOL_GREY.value)

        self.stdscr.attrset(curses.color_pair(SyntaxColors.TEXT.value))
        self.stdscr.bkgd(' ', curses.color_pair(SyntaxColors.TEXT.value))
        self.editorscr.bkgd(' ', curses.color_pair(SyntaxColors.TEXT.value))
        self.filenavscr.bkgd(' ', curses.color_pair(SyntaxColors.TEXT.value))
        self.filenavscr.refresh()

        self.linenumscr.attrset(curses.color_pair(SyntaxColors.LINE_NUMBER.value))
        self.linenumscr.bkgd(' ', curses.color_pair(SyntaxColors.LINE_NUMBER.value))

        # set up something bright for statusscr
        self.statusscr.bkgd(' ', curses.color_pair(SyntaxColors.STATUS.value))
        self.statusscr.attrset(curses.color_pair(SyntaxColors.STATUS.value))
        self.statusscr.refresh()

    def loadFile(self,fileName):
        with open(self.fileName, 'r') as f:
            self.fileLines = f.readlines()
        # making the linked list
        return(LineLinkedList(self.fileLines))

    def __init__(self):

        # set up curses stuff
        self.initScreens()
        self.birth()
        self.initColors()
        self.runFileNavigation(breakEarly = True)
        self.drawAndRefreshFileNavigation()

        # grabbing the lines from the file
        self.fileName = 'a.cpp'
        self.fileName = 'index.html'
        self.fileName = 'test.py'
        self.lineLinkedList = self.loadFile(self.fileName)

        # make and store the savefile here

        (maxY,maxX) = self.stdscr.getmaxyx()

        # setting ui up
        self.editorscr.move(0,0)
        self.currentLineCount = 0

        # keep 2 pointers; 1 for top line node, 1 for current line node
        self.topLine = self.currentLine = self.lineLinkedList.start
        self.topLineCount = 1 # number to draw for topLine
        self.currentLineIndex = 0

        self.drawLines()
        self.state = State.NORMAL

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
        #self.saveFile.close() # close the savefile

    def birth(self):
        curses.noecho()
        curses.cbreak()

    def kill(self):
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()

    def currentLineHeight(self):
        """
        Returns the height of the current line
        """
        return self.lineHeight(self.currentLine)

    def lineHeight(self, lineNode):
        """
        Returns the "height" (how many rows it takes up) of lineNode object passed in
        """
        # old implementation
        #manyLines = len(self.fileLines[lineNumber])//self.editorscr.getmaxyx()[1]+1
        #return manyLines if manyLines else 1
        manyLines = len(lineNode.value)//self.editorscr.getmaxyx()[1]+1
        return manyLines if manyLines else 1

    def getCurrentChar(self):
        return self.currentLine.value[self.currentLineIndex]

    def getNextChar(self):
        # note we are guaranteed to have this as we never get to newline char
        return self.currentLine.value[self.currentLineIndex+1]


    def moveToEndOfLine(self):
        self.currentLineIndex = len(self.currentLine.value)-2

    def moveToBeginningOfLine(self):
        self.currentLineIndex = 0

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

    def saveFile(self):
        """
        Saves all lines in lineLinkedList to the file with the name self.fileName in cwd
        """
        f = open(self.fileName, 'w')
        walk = self.lineLinkedList.start
        while walk != None:
            f.write(walk.value)
            walk = walk.nextNode

    def drawLines(self):
        """
        Takes in a scr object from which it draws on

        Draws the line numbers and the lines themselves onto the ui
        O(n) where n is the number of blocks that can fit onto the terminal, but since n is very small and theta(n) is a fraction of n usually < n/2 this is fine.
        """
        # clear the old data off of the screen
        self.linenumscr.clear()
        self.editorscr.clear()

        (moveY,moveX) = (0,0) # to move after


        # draw line numbers
        lineToDraw = self.topLine
        y = 0
        lineIndex = self.topLineCount
        self.linenumscr.move(0,0)
        while y < self.linenumscr.getmaxyx()[0]-1:
            self.linenumscr.addstr(str(lineIndex))

            if lineToDraw == self.currentLine:
                moveY = y + self.currentLineIndex//self.editorscr.getmaxyx()[1]
                moveX = min(self.currentLineIndex % self.editorscr.getmaxyx()[1], len(self.currentLine.value)-2) # avoid the newline char
                self.currentLineCount = lineIndex
                if moveX <= -1: moveX = 0

            y += self.lineHeight(lineToDraw)

            if lineToDraw.nextNode == None: # ran out of nodes
                break
            lineToDraw = lineToDraw.nextNode
            lineIndex += 1

            if y > self.linenumscr.getmaxyx()[0]-1:
                break
            self.linenumscr.move(y,0)

        # draw the lines themselves
        lineToDraw = self.topLine
        self.editorscr.move(0,0)
        cursorY = 0
        while lineToDraw != None:

            if self.editorscr.getyx()[0]+self.lineHeight(lineToDraw) > self.editorscr.getmaxyx()[0]-1: # handle unprintable text (no space at bottom) when scrolling up
                self.editorscr.addstr('@')
                break
            i = 0
            for c in lineToDraw.value:
                self.editorscr.addstr(c,curses.color_pair(lineToDraw.colors[i]))
                if self.editorscr.getyx()[1]+1 > self.editorscr.getmaxyx()[1]-1: # we have reached the end of the line horizontally
                    cursorY += 1
                    self.editorscr.move(cursorY,0)
                i += 1

            if self.editorscr.getyx()[0] + 1 > self.editorscr.getmaxyx()[0]-1:
                break
            self.editorscr.move(cursorY+1,0)
            cursorY += 1
            lineToDraw = lineToDraw.nextNode

        # testing
        #self.filenavscr.clear()
        #self.filenavscr.addstr(str((self.currentLineIndex,self.getCurrentChar())))
        #self.filenavscr.refresh()

        # move cursor to where it should be as specified by currentLine and currentLineIndex, refresh and move on
        self.editorscr.move(moveY,moveX)
        self.linenumscr.refresh()
        self.editorscr.refresh()

    def drawStatus(self):
        """
        Draws status using whatever is set as default
        """
        self.statusscr.clear()
        checkStr = (self.getStateStr()+'  '+os.getcwd()+'/'+self.fileName+'  '+
            'Line '+str(self.currentLineCount)+' Column '+str(self.currentLineIndex))
        if len(checkStr) > self.statusscr.getmaxyx()[1]:
            checkStr = checkStr[:self.statusscr.getmaxyx()[1]-2]
        self.statusscr.addstr(checkStr)
        self.statusscr.refresh()

    def getCmd(self):
        """
        Get command from user when in command mode
        """
        cmdStr = ':'
        c = ''
        while c != '\n':
            if c == chr(127): # backspace
                cmdStr = cmdStr[:-1]
            elif c == chr(27): # escape
                return chr(27)
            else:
                cmdStr += c

            self.cmdlinescr.clear()
            self.cmdlinescr.addstr(cmdStr)
            self.cmdlinescr.refresh()
            c = chr(self.cmdlinescr.getch())
        return cmdStr

    def getStateStr(self):
        if self.state == State.NORMAL:
            return 'NORMAL'
        elif self.state == State.INSERT:
            return 'INSERT'
        elif self.state == State.VISUAL:
            return 'VISUAL'
        elif self.state == State.COMMAND_LINE:
            return 'CMD_LINE'
        elif self.state == State.FILE_NAVIGATION:
            return 'FILE_NAV'
        else:
            return 'UNKNOWN_STATE'


    def moveDown(self,y,x):
        """
        Moves down one line
        """
        if self.currentLine.nextNode == None: # we don't have any more nodes
            return
        if y+self.lineHeight(self.currentLine) < self.editorscr.getmaxyx()[0]-2:
            self.currentLine = self.currentLine.nextNode
            if self.currentLineIndex > len(self.currentLine.value) - 2:
                self.currentLineIndex = len(self.currentLine.value) - 2
                self.drawLines()
            if self.currentLineIndex < 0:
                self.currentLineIndex = 0

        elif self.currentLine.nextNode != None:
            self.currentLine = self.currentLine.nextNode
            amountToMoveDown = self.lineHeight(self.currentLine)
            while amountToMoveDown > 0:
                amountToMoveDown -= self.lineHeight(self.topLine)
                self.topLine = self.topLine.nextNode
                self.topLineCount += 1


    def moveUp(self,y,x):
        if y > 0:
            self.currentLine = self.currentLine.lastNode
            if self.currentLineIndex > len(self.currentLine.value) - 2:
                self.currentLineIndex = len(self.currentLine.value) - 2
                if self.currentLineIndex < 0:
                    self.currentLineIndex = 0
                self.drawLines()
        elif self.currentLine.lastNode != None:
            self.currentLine = self.currentLine.lastNode
            #self.kill()
            #print(self.currentLine.value)
            #assert(False)
            self.topLine = self.topLine.lastNode
            self.topLineCount -= 1

    def moveLeft(self,y,x):
        if self.editorscr.getyx()[1] > 0:
            if self.currentLineIndex > len(self.currentLine.value)-2:
                self.currentLineIndex = len(self.currentLine.value)-2
            if self.currentLineIndex > 0:
                self.currentLineIndex -= 1
        else:
            if self.currentLineIndex > 0:
                self.currentLineIndex -= 1

    def moveRight(self,y,x):
        if self.currentLine.value != '\n': # if it's only newline ignore
            if self.currentLineIndex > len(self.currentLine.value) - 2:
                self.currentLineIndex = len(self.currentLine.value) - 2

            if self.currentLine.value[self.currentLineIndex+1] != '\n':
                self.currentLineIndex += 1

    def outputChatter(self,process):
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
            if out == '' and process.poll() != None:
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
                self.drawLines()
                self.editorscr.refresh()

        # kill the pipe
        process.stdout.close()

        # now wait for the user to send some ready confirmation that he's seen the output and he's good to go
        self.statusscr.clear()
        self.statusscr.addstr('Please press any key to proceed.')
        self.statusscr.refresh()

        self.editorscr.getch() # wait for confirmation

        # set the old lines and topline back
        self.lineLinkedList = tempLinkedList
        self.topLine = tempPointer

        self.drawLines()
        self.editorscr.refresh()


    def setUpSyntaxHighlighting(self):
        pylex = Python3Lexer()
        # lets build the string to parse
        syntax = ''
        walk = self.lineLinkedList.start
        while walk != None:
            syntax += walk.value
            walk = walk.nextNode

        walk = self.lineLinkedList.start

        #self.kill()
        #for token in pylex.get_tokens(syntax):
        #    print(token)
        #assert(False)

        i = 0 # index of where i am walking through the string

        for token in pylex.get_tokens(syntax):

            if token[1] == '\n':
                walk = walk.nextNode
                i = -1
                if walk == None:
                    break

            tokenType = SyntaxColors.TEXT.value # assume everything is text and find contradiction

            if pygments.token.Comment.Single == token[0]:
                tokenType = SyntaxColors.COMMENT.value

            if pygments.token.Keyword.Namespace == token[0]:
                tokenType = SyntaxColors.NAMESPACE.value

            if pygments.token.Keyword == token[0]:
                tokenType = SyntaxColors.KEYWORD.value

            if pygments.token.Name.Builtin == token[0]:
                tokenType = SyntaxColors.BUILTIN.value

            if pygments.token.Name.Function == token[0]:
                tokenType = SyntaxColors.FUNCTION.value

            if pygments.token.Literal.Number.Integer == token[0] or pygments.token.Literal.Number.Float == token[0]:
                tokenType = SyntaxColors.LITERAL.value

            if pygments.token.Operator == token[0]:
                tokenType = SyntaxColors.OPERATOR.value

            if pygments.token.Literal.String.Single == token[0]:
                tokenType = SyntaxColors.STRING_LITERAL.value

            for c in token[1]:
                walk.colors[i] = tokenType
                i += 1

    def drawAndRefreshFileNavigation(self):

        self.filenavscr.clear()

        # draw the directory
        (oldY,oldX) = self.filenavscr.getyx()
        y = 0
        self.filenavscr.move(y,0)

        for i in range(self.topDir, len(self.dirs)):
            directory = self.dirs[i]

            # handle coloring
            color = SyntaxColors.FILE.value # assume everything is a file
            if os.path.isdir(directory):
                color = SyntaxColors.FOLDER.value

            self.filenavscr.addstr(directory,curses.color_pair(color))
            y += 1
            if y > self.filenavscr.getmaxyx()[0]-1:
                y -= 1
                self.filenavscr.move(y,0)
                for c in range(self.filenavscr.getmaxyx()[1]-2):
                        self.filenavscr.addstr(' ')
                self.filenavscr.move(y,0)
                self.filenavscr.addstr('...')
                break
            self.filenavscr.move(y,0)

        self.filenavscr.move(oldY,oldX)
        self.filenavscr.refresh()

    def getDirs(self):
        dirs = ['..']+sorted(os.listdir())
        i = 1
        for directory in dirs[1:]:
            if '.' == directory[0]:
                dirs.append(dirs.pop(i))
                i -= 1
            i += 1
        return dirs

    def runFileNavigation(self, breakEarly = False):

        self.dirs = self.getDirs()
        self.topDir = 0
        self.drawAndRefreshFileNavigation()
        self.filenavscr.move(0,0)

        y = 0

        while True:

            if breakEarly:
                self.state = State.NORMAL
                break

            c = chr(self.filenavscr.getch())

            if c == '`':
                self.state = State.NORMAL
                break

            if c == 'k':
                y -= 1
                if y < 0:
                    y += 1

            if c == 'j':
                y += 1
                if y > len(self.dirs)-1  or y > self.filenavscr.getmaxyx()[0]-2:
                    if y > self.filenavscr.getmaxyx()[0]-2:
                        self.topDir += 1
                    y -= 1

            if c == '\n':
                try:
                    os.chdir(self.dirs[self.topDir+y])
                    self.dirs = self.getDirs()
                except:
                    self.fileName = self.dirs[self.topDir+y]
                    self.lineLinkedList = self.loadFile(self.fileName)
                    self.topLine = self.currentLine = self.lineLinkedList.start
                    self.currentLineIndex = 0
                    self.setUpSyntaxHighlighting()
                    self.drawLines()
                y = 0

            self.drawAndRefreshFileNavigation()
            self.filenavscr.move(y,0)


    def run(self):
        """
        Main loop of the state machine
        """
        while True:

            self.setUpSyntaxHighlighting()

            self.drawStatus() # draw the status bar text on status bar
            self.drawLines()
            (y,x) = self.editorscr.getyx() # get cursor position relative to top left
            if self.state == State.NORMAL:
                c = chr(self.editorscr.getch()) #get a key

                # movement
                # remember top left is (0,0)
                if c == 'j': # down
                    self.moveDown(y,x)
                elif c == 'k': # up
                    self.moveUp(y,x)
                elif c == 'h': # left
                    self.moveLeft(y,x)
                elif c == 'l': # right
                    self.moveRight(y,x)
                elif c == '$': # eol
                    self.moveToEndOfLine()
                elif c == '0': # beginning
                    self.moveToBeginningOfLine()

                elif c == 'w':
                    """
                    Walk through elements on line until you hit either punctuation (where you stop) or spaces (where you walk through until you hit something that isn't a space)
                    """

                    # handle edge case of `w` on '\n' line
                    if self.currentLine.value == '\n' or self.getNextChar() == '\n':
                        self.moveDown(y,x)
                        self.currentLineIndex = 0
                        continue

                    while True:

                        self.moveRight(y,x)
                        self.drawLines()
                        c = self.getCurrentChar()

                        if c in self.punctuationChars:
                            break

                        if self.getNextChar() == '\n':
                            break
                            self.moveDown(y,0)
                            self.currentLineIndex = 0
                            self.drawLines()
                            c = self.getCurrentChar()
                            break

                        if c == ' ':
                            while c == ' ':
                                self.moveRight(y,x)
                                self.drawLines()
                                c = self.getCurrentChar()
                                if self.getNextChar() == '\n':
                                    break
                            break

                elif c == 'e':
                    # handle edge case of `e` on '\n' line
                    if self.currentLine.value == '\n' or self.getNextChar() == '\n':
                        self.moveDown(y,x)
                        self.currentLineIndex = 0
                        continue

                    self.moveRight(y,x)

                    while True:
                        while self.getNextChar() == ' ':
                            self.moveRight(y,x)
                        while self.getNextChar() in string.ascii_letters:
                            self.moveRight(y,x)
                        self.drawLines()

                        break


                elif c == 'b':
                    """
                    Walk through elements on the line _backwards_ until the character before is punctuation or a space
                    """

                    moveForward = True
                    self.moveLeft(y,x)
                    self.currentLineIndex -= 1
                    if self.currentLineIndex < 0:
                        if self.currentLine.lastNode == None:
                            self.currentLineIndex = 0
                            continue
                        #self.currentLine = self.currentLine.lastNode
                        self.moveUp(y,x)
                        self.moveToEndOfLine()
                        self.drawLines()
                        self.currentLineIndex = 0

                    if len(self.currentLine.value) <= 2:
                        continue

                    # now we are guaranteed a line with at least two characters
                    c = self.getCurrentChar()

                    while c == ' ':
                        self.moveLeft(y,x)
                        self.drawLines()
                        c = self.getCurrentChar()
                        if c in self.punctuationChars:
                            moveForward = False
                            break
                        if self.editorscr.getyx()[1] == 0:
                            if self.currentLine == 0:
                                moveForward = False
                                break
                            self.moveUp(y,x)
                            self.drawLines()
                            self.moveToEndOfLine()
                            self.drawLines()

                    while c in string.ascii_letters or c in string.digits:
                        self.moveLeft(y,x)
                        self.drawLines()
                        c = self.getCurrentChar()
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
                        self.moveRight(y,x)
                        self.drawLines()

                # move to different states
                elif c == 'i':
                    self.state = State.INSERT

                elif c == 'a':
                    if self.getNextChar() == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    self.moveRight(y,x)
                    self.drawLines()
                    self.state = State.INSERT

                elif c == 'A':
                    self.moveToEndOfLine()
                    if self.getNextChar() == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    self.moveRight(y,x)
                    self.drawLines()
                    self.state = State.INSERT

                elif c == 'v':
                    self.state = State.VISUAL

                elif c == ':':
                    self.state = State.COMMAND_LINE

                elif c == '`':
                    self.state = State.FILE_NAVIGATION

            if self.state == State.INSERT:

                c = chr(self.editorscr.getch())

                if ord(c) == 23: # ctrl + w
                    # save file
                    # don't do it like this, use vim-like command
                    self.saveFile()

                if ord(c) == 27: # escape
                    self.moveLeft(y,x)
                    self.state = State.NORMAL

                elif ord(c) == 127: # backspace
                    self.currentLine.value = self.currentLine.value[:max(self.currentLineIndex-1,0)]+self.currentLine.value[max(self.currentLineIndex,0):]
                    self.currentLineIndex -= 1
                    self.colors = self.currentLine.colors[:-1]
                    if self.currentLineIndex == -1:
                        # delete the line
                        self.currentLine = self.deleteLine(self.currentLine)
                        self.drawLines()

                elif ord(c) == 10: # enter
                    self.currentLine = self.insertLine(self.currentLine)
                    self.moveToBeginningOfLine()
                    self.drawLines()

                else: # any other character
                    self.currentLine.value = self.currentLine.value[:self.currentLineIndex] + c + self.currentLine.value[self.currentLineIndex:]
                    self.currentLineIndex += 1
                    self.currentLine.colors.append(0)
                    self.drawLines()


            elif self.state == State.VISUAL:
                self.state = State.NORMAL

            elif self.state == State.COMMAND_LINE:
                # what about if user presses escape?
                cmd = self.getCmd()
                if cmd == chr(27): # escape character
                    self.state = State.NORMAL
                    continue
                cmd = cmd.strip(' \t\n\r')
                # tokenize based on '|'
                cmds = cmd.split('|')
                #self.kill()
                #print(cmds)
                #assert(False)
                for cmd in cmds:
                    for cmdChar in cmd:
                        if cmdChar == 'w':
                            self.saveFile()
                        if cmdChar == 'q':
                            sys.exit(0)
                        if cmdChar == '!':
                            # clear the screens to prep
                            self.stdscr.clear()
                            self.editorscr.clear()
                            self.linenumscr.clear()

                            # kill the process to give stdin pipe back to terminal
                            self.kill()

                            if cmd[0] == ':':
                                cmd = cmd[1:]
                            if cmd[0] == '!':
                                cmd = cmd[1:]

                            process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)

                            self.outputChatter(process)

                            # bring what we killed back to life
                            self.birth()

                # set state to normal upon exit
                self.state = State.NORMAL

            elif self.state == State.FILE_NAVIGATION:
                self.runFileNavigation()



if __name__ == "__main__":
    editor = MainScr()
    editor.run()
