import string # ascii, digits lists
import os # for file subsystem (os.chdir, os.getcwd, etc)
import sys # for sys.exit
import subprocess # for BANG!
import threading
import time

import curses # drawing the editor
from pygments.lexers import Python3Lexer
import pygments

from dataStructures.lineLinkedList import LineLinkedList
from dataStructures.lineNode import LineNode
from Util.initCurses import initColors, initScreens
from constants import State, NormalState, SyntaxColors, Colors, WindowConstants
import Util.fileUtil as fileUtil
import Util.editorUtil as editorUtil
import Util.cursesUtil as cursesUtil
import Util.syntaxHighlighting as syntaxHighlighting
from algorithms.binSearch import dirBinSearch

class MainScr:

    def __init__(self):

        # set up curses stuff
        initScreens(self,WindowConstants)
        cursesUtil.birth()

	# init all the colors
        initColors(SyntaxColors, Colors)
        self.stdscr.attrset(curses.color_pair(SyntaxColors.TEXT.value))
        self.stdscr.bkgd(' ', curses.color_pair(SyntaxColors.TEXT.value))
        self.editorscr.bkgd(' ', curses.color_pair(SyntaxColors.TEXT.value))
        self.filenavscr.bkgd(' ', curses.color_pair(SyntaxColors.TEXT.value))
        self.filenavscr.refresh()

        self.linenumscr.attrset(curses.color_pair(SyntaxColors.LINE_NUMBER.value))
        self.linenumscr.bkgd(' ', curses.color_pair(SyntaxColors.LINE_NUMBER.value))

        self.runFileNavigation(breakEarly = True)
        self.drawAndRefreshFileNavigation()

        # grabbing the lines from the file
        self.fileName = 'test.py'
        self.lineLinkedList = fileUtil.loadFile(self.fileName)

        # make and store the savefile here

        (maxY,maxX) = self.stdscr.getmaxyx()

        # setting ui up
        self.editorscr.move(0,0)
        self.currentLineCount = 0

        # set up something bright for statusscr
        self.statusscr.bkgd(' ', curses.color_pair(SyntaxColors.STATUS.value))
        self.statusscr.attrset(curses.color_pair(SyntaxColors.STATUS.value))
        self.statusscr.refresh()

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

            y += editorUtil.lineHeight(self,lineToDraw)

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

            if self.editorscr.getyx()[0]+editorUtil.lineHeight(self,lineToDraw) > self.editorscr.getmaxyx()[0]-1: # handle unprintable text (no space at bottom) when scrolling up
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
        if y+editorUtil.lineHeight(self,self.currentLine) < self.editorscr.getmaxyx()[0]-2:
            self.currentLine = self.currentLine.nextNode
            if self.currentLineIndex > len(self.currentLine.value) - 2:
                self.currentLineIndex = len(self.currentLine.value) - 2
                self.drawLines()
            if self.currentLineIndex < 0:
                self.currentLineIndex = 0

        elif self.currentLine.nextNode != None:
            self.currentLine = self.currentLine.nextNode
            amountToMoveDown = editorUtil.lineHeight(self,self.currentLine)
            while amountToMoveDown > 0:
                amountToMoveDown -= editorUtil.lineHeight(self,self.topLine)
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

    def outputTerminalChatter(self,process):
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

            try:
                self.filenavscr.addstr('- '+directory,curses.color_pair(color))
            except:
                continue

            y += len(directory)//(self.filenavscr.getmaxyx()[1]-1)+1

            if y > self.filenavscr.getmaxyx()[0]-1:
                y -= len(directory)//self.editorscr.getmaxyx()[1]+1
                self.filenavscr.move(y,0)
                for c in range(self.filenavscr.getmaxyx()[1]-2):
                        self.filenavscr.addstr(' ')
                self.filenavscr.move(y,0)
                self.filenavscr.addstr('...')
                break
            self.filenavscr.move(y,0)

        self.filenavscr.move(oldY,oldX)
        self.filenavscr.refresh()

    def runFileNavigation(self, breakEarly = False):


        self.dirs = editorUtil.getDirs(self)
        self.topDir = 0
        self.currentDir = 0
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
                y -= (len(self.dirs[self.currentDir-1]))//(self.filenavscr.getmaxyx()[1])+1
                # remember you have ' -' at the start of every dir
                if y < 0:
                    self.topDir -= 1
                    if self.topDir < 0:
                        self.topDir += 1
                        self.currentDir += 1
                    y += (len(self.dirs[self.currentDir-1]))//(self.filenavscr.getmaxyx()[1])+1
                self.currentDir -= 1

            elif c == 'j':
                y += (len(self.dirs[self.currentDir]))//(self.filenavscr.getmaxyx()[1])+1
                if self.currentDir + 1 == len(self.dirs):
                    y -= (len(self.dirs[self.currentDir])+1)//(self.filenavscr.getmaxyx()[1])+1
                    continue

                if y > self.filenavscr.getmaxyx()[0]-2:
                    y -= len(self.dirs[self.currentDir])//(self.filenavscr.getmaxyx()[1])+1
                    self.topDir += 1

                self.currentDir += 1


            elif c == '\n':
                try:
                    os.chdir(self.dirs[self.currentDir])
                    self.dirs = editorUtil.getDirs(self)
                    self.currentDir = 0
                    self.topDir = 0

                except:
                    # reload file and prep
                    self.fileName = self.dirs[self.currentDir]
                    self.lineLinkedList = fileUtil.loadFile(self.fileName)
                    self.topLine = self.currentLine = self.lineLinkedList.start
                    self.currentLineIndex = 0
                    syntaxHighlighting.setColors(self)
                    self.drawLines()

                    # reset file dir
                    self.currentDir = 0
                    self.topDir = 0
                y = 0

            elif c == '?':
                searchSubStr = editorUtil.getCmd(self,getSearch = True)[1:]
                searchSubStr = searchSubStr.lstrip()
                if searchSubStr == chr(27):
                    continue
                else:
                    self.currentDir = dirBinSearch(self.dirs, searchSubStr, self.currentDir)
                    self.topDir = self.currentDir - self.currentDir % self.filenavscr.getmaxyx()[0]
                    y = 0
                    walk = self.topDir
                    while walk != self.currentDir:
                        y += len(self.dirs[walk])//(self.filenavscr.getmaxyx()[1])+1
                        walk += 1


            self.drawAndRefreshFileNavigation()
            self.filenavscr.move(y,0)

    def run(self):
        """
        Main loop of the state machine
        """
        while True:

            syntaxHighlighting.setColors(self)

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
                    editorUtil.moveToEndOfLine(self)
                elif c == '0': # beginning
                    editorUtil.moveToBeginningOfLine(self)

                elif c == 'w':
                    """
                    Walk through elements on line until you hit either punctuation (where you stop) or spaces (where you walk through until you hit something that isn't a space)
                    """

                    # handle edge case of `w` on '\n' line
                    if self.currentLine.value == '\n' or editorUtil.getNextChar(self) == '\n':
                        self.moveDown(y,x)
                        self.currentLineIndex = 0
                        continue

                    while True:

                        self.moveRight(y,x)
                        self.drawLines()
                        c = editorUtil.getCurrentChar(self)

                        if c in self.punctuationChars:
                            break

                        if editorUtil.getNextChar(self) == '\n':
                            break
                            self.moveDown(y,0)
                            self.currentLineIndex = 0
                            self.drawLines()
                            c = editorUtil.getCurrentChar(self)
                            break

                        if c == ' ':
                            while c == ' ':
                                self.moveRight(y,x)
                                self.drawLines()
                                c = editorUtil.getCurrentChar(self)
                                if editorUtil.getNextChar(self) == '\n':
                                    break
                            break

                elif c == 'e':
                    # handle edge case of `e` on '\n' line
                    if self.currentLine.value == '\n' or editorUtil.getNextChar(self) == '\n':
                        self.moveDown(y,x)
                        self.currentLineIndex = 0
                        continue

                    self.moveRight(y,x)

                    while True:
                        while editorUtil.getNextChar(self) == ' ':
                            self.moveRight(y,x)
                        while editorUtil.getNextChar(self) in string.ascii_letters:
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
                        self.moveUp(y,x)
                        editorUtil.moveToEndOfLine(self)
                        self.drawLines()
                        self.currentLineIndex = 0

                    if len(self.currentLine.value) <= 2:
                        continue

                    # now we are guaranteed a line with at least two characters
                    c = editorUtil.getCurrentChar(self)

                    while c == ' ':
                        self.moveLeft(y,x)
                        self.drawLines()
                        c = editorUtil.getCurrentChar(self)
                        if c in self.punctuationChars:
                            moveForward = False
                            break
                        if self.editorscr.getyx()[1] == 0:
                            if self.currentLine == 0:
                                moveForward = False
                                break
                            self.moveUp(y,x)
                            self.drawLines()
                            editorUtil.moveToEndOfLine(self)
                            self.drawLines()

                    while c in string.ascii_letters or c in string.digits:
                        self.moveLeft(y,x)
                        self.drawLines()
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
                        self.moveRight(y,x)
                        self.drawLines()

                # move to different states
                elif c == 'i':
                    self.state = State.INSERT

                elif c == 'a':
                    if editorUtil.getNextChar(self) == '\n':
                        self.currentLine.value = self.currentLine.value[:self.currentLineIndex+1] + ' \n'
                        self.currentLine.colors.append(0)
                        # insert a space
                    self.moveRight(y,x)
                    self.drawLines()
                    self.state = State.INSERT

                elif c == 'A':
                    editorUtil.moveToEndOfLine(self)
                    if editorUtil.getNextChar(self) == '\n':
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
                    fileUtil.saveFile(self)

                if ord(c) == 27: # escape
                    self.moveLeft(y,x)
                    self.state = State.NORMAL

                elif ord(c) == 127: # backspace
                    self.currentLine.value = self.currentLine.value[:max(self.currentLineIndex-1,0)]+self.currentLine.value[max(self.currentLineIndex,0):]
                    self.currentLineIndex -= 1
                    self.colors = self.currentLine.colors[:-1]
                    if self.currentLineIndex == -1:
                        # delete the line
                        self.currentLine = editorUtil.deleteLine(self,self.currentLine)
                        self.drawLines()

                elif ord(c) == 10: # enter
                    self.currentLine = editorUtil.insertLine(self,self.currentLine)
                    editorUtil.moveToBeginningOfLine(self)
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
                cmd = editorUtil.getCmd(self)
                if cmd == chr(27): # escape character
                    self.state = State.NORMAL
                    continue
                cmd = cmd.strip(' \t\n\r')
                # tokenize based on '|'
                cmds = cmd.split('|')
                for cmd in cmds:
                    for cmdChar in cmd:
                        if cmdChar == 'w':
                            fileUtil.saveFile(self)
                        if cmdChar == 'q':
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

                            process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)

                            self.outputTerminalChatter(process)

                            # bring what we killed back to life
                            cursesUtil.birth()

                # set state to normal upon exit
                self.state = State.NORMAL

            elif self.state == State.FILE_NAVIGATION:
                self.runFileNavigation()



if __name__ == "__main__":
    editor = MainScr()
    editor.run()
