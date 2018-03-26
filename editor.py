# look into "wrapper" for debugging

from enum import Enum
import string # ascii, digits lists
import os # for file subsystem (os.chdir, os.getcwd, etc)
import sys # for sys.exit
import subprocess # for BANG!
import threading
import time

import curses # drawing the editor

from lineLinkedList import LineLinkedList
from lineNode import LineNode

class State(Enum):
    NORMAL = 0
    INSERT = 1
    VISUAL = 2
    COMMAND_LINE = 3

class NormalState(Enum):
    MOVEMENT = 0
    DELETE = 1
    # what else do I need

class ColorSchemes(Enum):
    # for the syntax highlighter mostly
    pass

MAX_LINE_NUMBER_LENGTH = 4
FILE_SUBSYSTEM_WINDOW_LENGTH = 18

class Editor:

    def __init__(self):
        # handling curses
        # init screens
        self.stdscr = curses.initscr()
        self.editorscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, self.stdscr.getmaxyx()[1]-(MAX_LINE_NUMBER_LENGTH+1)-FILE_SUBSYSTEM_WINDOW_LENGTH, 0, MAX_LINE_NUMBER_LENGTH+1+FILE_SUBSYSTEM_WINDOW_LENGTH)
        self.linenumscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, MAX_LINE_NUMBER_LENGTH+1, 0, FILE_SUBSYSTEM_WINDOW_LENGTH)
        self.filenavscr = curses.newwin(self.stdscr.getmaxyx()[0], FILE_SUBSYSTEM_WINDOW_LENGTH, 0, 0)
        self.statusscr = curses.newwin(1,self.stdscr.getmaxyx()[1]-FILE_SUBSYSTEM_WINDOW_LENGTH, self.stdscr.getmaxyx()[0]-2, FILE_SUBSYSTEM_WINDOW_LENGTH)
        self.cmdlinescr = curses.newwin(1,self.stdscr.getmaxyx()[1]-FILE_SUBSYSTEM_WINDOW_LENGTH, self.stdscr.getmaxyx()[0]-1, FILE_SUBSYSTEM_WINDOW_LENGTH)

        # set up curses stuff and colors
        curses.noecho()
        curses.cbreak()
        curses.start_color() # have to make exceptions for terminals that don't support color
        curses.init_color(0, 125, 100, 90) # cool grey
        curses.init_color(5, 400, 400, 400) # medium grey
        curses.init_color(1, 1000, 1000, 1000) # white
        curses.init_pair(1, 1, 0)
        self.stdscr.attrset(curses.color_pair(1))
        curses.init_pair(3, 5, 0) # lighter grey text, cool grey background
        self.linenumscr.attrset(curses.color_pair(3))

        # set up something bright for statusscr
        curses.init_color(2, 0, 0, 0) # black
        curses.init_pair(2, 0, 1)
        self.statusscr.bkgd(' ', curses.color_pair(2))
        self.statusscr.attrset(curses.color_pair(2))
        self.statusscr.refresh() # apply color

        # grabbing the lines from the file
        #self.fileName = 'a.cpp'
        self.fileName = 'index.html'
        with open(self.fileName, 'r+') as f:
            self.fileLines = f.readlines()
        # making the linked list
        self.lineLinkedList = LineLinkedList(self.fileLines)

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

        # testing

        #self.kill()
        #walk = self.lineLinkedList.start
        #while walk.nextNode != None:
        #    print(walk.value,end='')
        #    walk = walk.nextNode
        #assert(False)

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
            if lineToDraw.value == 'using namespace std;\n' and lineToDraw.lastNode.value == 'using\n':
                assert(False)
            for c in lineToDraw.value:
                self.editorscr.addstr(c)
                if self.editorscr.getyx()[1]+1 > self.editorscr.getmaxyx()[1]-1: # we have reached the end of the line horizontally
                    cursorY += 1
                    self.editorscr.move(cursorY,0)
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
        self.statusscr.clear()
        checkStr = (self.getStateStr()+'  '+os.getcwd()+'/'+self.fileName+'  '+
            'Line '+str(self.currentLineCount)+' Column '+str(self.currentLineIndex))
        if len(checkStr) > self.statusscr.getmaxyx()[1]:
            checkStr = checkStr[:self.statusscr.getmaxyx()[1]-2]
        self.statusscr.addstr(checkStr)
        self.statusscr.refresh()

    def getCmd(self):
        cmdStr = ':'
        c = ''
        while c != '\n':
            if c == chr(127):
                cmdStr = cmdStr[:-1]
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
        if self.state == State.INSERT:
            return 'INSERT'
        if self.state == State.VISUAL:
            return 'VISUAL'
        if self.state == State.COMMAND_LINE:
            return 'CMD_LINE'
        assert(False)


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



    def run(self):
        """
        Main loop of the state machine
        """
        while True:
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
                elif c == 'v':
                    self.state = State.VISUAL
                elif c == ':':
                    self.state = State.COMMAND_LINE

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
                    if self.currentLineIndex == -1:
                        # delete the line
                        self.currentLine = self.deleteLine(self.currentLine)
                        s = self.currentLine.value
                        self.drawLines()

                elif ord(c) == 10: # enter
                    self.currentLine = self.insertLine(self.currentLine)
                    self.moveToBeginningOfLine()
                    self.drawLines()

                else: # any other character
                    self.currentLine.value = self.currentLine.value[:-2]+' \n'
                    self.currentLine.value = self.currentLine.value[:self.currentLineIndex] + c + self.currentLine.value[self.currentLineIndex:]
                    self.currentLineIndex += 1
                    self.drawLines()


            if self.state == State.VISUAL:
                self.state = State.NORMAL

            if self.state == State.COMMAND_LINE:
                cmd = self.getCmd()
                cmd = cmd.strip(' \t\n\r')
                # tokenize based on ' | '
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
                            self.stdscr.clear()
                            self.editorscr.clear()
                            self.linenumscr.clear()
                            self.kill()

                            if cmd[0] == ':':
                                cmd = cmd[1:]
                            if cmd[0] == '!':
                                cmd = cmd[1:]

                            process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)

                            self.outputChatter(process)

                self.state = State.NORMAL

if __name__ == "__main__":
    editor = Editor()
    editor.run()
