
# look into "wrapper" for debugging

from enum import Enum
import linecache
import string

import curses

from lineLinkedList import LineLinkedList


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
        self.stdscr = curses.initscr()
        self.editorscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, self.stdscr.getmaxyx()[1]-(MAX_LINE_NUMBER_LENGTH+1)-FILE_SUBSYSTEM_WINDOW_LENGTH, 0, MAX_LINE_NUMBER_LENGTH+1+FILE_SUBSYSTEM_WINDOW_LENGTH)
        self.linenumscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, MAX_LINE_NUMBER_LENGTH+1, 0, FILE_SUBSYSTEM_WINDOW_LENGTH)
        self.filenavscr = curses.newwin(self.stdscr.getmaxyx()[0], FILE_SUBSYSTEM_WINDOW_LENGTH, 0, 0)
        self.filenavscr.refresh()
        curses.noecho()
        curses.cbreak()
        curses.start_color() # have to make exceptions for terminals that don't support color
        curses.init_color(0, 125, 100, 90)
        curses.init_color(1, 1000, 1000, 1000)
        curses.init_pair(1, 1, 0)
        self.stdscr.attrset(curses.color_pair(1))
        self.linenumscr.attrset(curses.color_pair(1))

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
        # old implementation
        #self.currentLine = 0
        #self.currentLineIndex = 0
        #self.topLine = 0

        # keep 2 pointers; 1 for top line node, 1 for current line node
        self.topLine = self.currentLine = self.lineLinkedList.start
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
        self.saveFile.close() # close the savefile

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
        self.linenumscr.move(0,0)
        while y < self.linenumscr.getmaxyx()[0]-1:
            self.linenumscr.addstr(str(lineToDraw.index+1))

            if lineToDraw == self.currentLine:
                moveY = y + self.currentLineIndex//self.editorscr.getmaxyx()[1]
                moveX = min(self.currentLineIndex % self.editorscr.getmaxyx()[1], len(self.currentLine.value)-2) # avoid the newline char
                if moveX <= -1: moveX = 0

            y += self.lineHeight(lineToDraw)
            if lineToDraw.nextNode == None: # ran out of nodes
                break 
            lineToDraw = lineToDraw.nextNode
            if y > self.linenumscr.getmaxyx()[0]-1:
                break
            self.linenumscr.move(y,0)




        # draw the lines themselves
        lineToDraw = self.topLine
        self.editorscr.move(0,0)
        cursorY = 0
        while True:
            if self.editorscr.getyx()[0]+self.lineHeight(lineToDraw) > self.editorscr.getmaxyx()[0]-1: # handle unprintable text (no space at bottom) when scrolling up
                self.editorscr.addstr('@')
                break
            for c in lineToDraw.value:
                self.editorscr.addstr(c)
                if self.editorscr.getyx()[1]+1 > self.editorscr.getmaxyx()[1]-1: # we have reached the end of the line horizontally
                    cursorY += 1
                    self.editorscr.move(cursorY,0)
            if self.editorscr.getyx()[0] + 1 > self.editorscr.getmaxyx()[0]-1:
                break
            self.editorscr.move(cursorY+1,0)
            cursorY += 1
            if lineToDraw.nextNode == None:
                break
            lineToDraw = lineToDraw.nextNode


        # testing
        self.filenavscr.clear()
        self.filenavscr.addstr(str((self.currentLineIndex,self.getCurrentChar())))
        self.filenavscr.refresh()

        # move cursor to where it should be as specified by currentLine and currentLineIndex, refresh and move on
        self.editorscr.move(moveY,moveX)
        self.linenumscr.refresh()
        self.editorscr.refresh()


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

        elif self.lineLinkedList.length - self.currentLine.index > 1:
            self.currentLine = self.currentLine.nextNode
            amountToMoveDown = self.lineHeight(self.currentLine)
            while amountToMoveDown > 0:
                amountToMoveDown -= self.lineHeight(self.topLine)
                self.topLine = self.topLine.nextNode


    def moveUp(self,y,x):
        if y > 0:
            self.currentLine = self.currentLine.lastNode
            if self.currentLineIndex > len(self.currentLine.value) - 2:
                self.currentLineIndex = len(self.currentLine.value) - 2
                self.drawLines()
        elif self.currentLine.lastNode != None:
            self.currentLine = self.currentLine.lastNode
            self.topLine = self.topLine.lastNode

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


    def run(self):
        """
        Main loop of the state machine
        """
        while True:
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

                # jumping movement
                elif c == 'w': 
                    """
                    Walk through elements on line until you hit either punctuation (where you stop) or spaces (where you walk through until you hit something that isn't a space)
                    """
                    
                    # handle edge case of `w` on '\n' line
                    if self.currentLine.value == '\n':
                        self.moveDown(y,x)
                        self.currentLineIndex = 0
                        continue

                    if self.getNextChar() == '\n':
                        self.moveDown(y,0)
                        self.currentLineIndex = 0
                        self.drawLines()

                    while True:
                        if self.currentLine.value == '\n':
                            break

                        self.moveRight(y,x)
                        self.drawLines()
                        c = self.getCurrentChar()

                        if c in self.punctuationChars:
                            break

                        if self.getNextChar() == '\n':
                            self.moveDown(y,0)
                            self.currentLineIndex = 0
                            self.drawLines()
                            c = self.getCurrentChar()

                        if c == ' ':
                            while c == ' ':
                                self.moveRight(y,x)
                                self.drawLines()
                                c = self.getCurrentChar()

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
                        self.currentLine = self.currentLine.lastNode
                        self.moveToEndOfLine()
                        self.drawLines()
                    
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
                    pass
                    self.state = State.COMMAND_LINE

            if self.state == State.INSERT:
                c = chr(self.editorscr.getch())
                s = self.fileLines[self.currentLine]
                if s[-1] != ' ':
                    s += ' '
                self.fileLines[self.currentLine] = s
                self.moveRight(y,x)
                self.drawLines()

                #self.kill()
                #print(ord(c))
                #assert(False)

                if ord(c) == 27: # escape
                    self.state = State.NORMAL
                    if self.fileLines[self.currentLine][-1] == ' ':
                        self.fileLines[self.currentLine] = self.fileLines[self.currentLine][-1]
                elif ord(c) == 127: # backspace
                    s = s[:self.currentLineIndex-2]+s[self.currentLineIndex-1:]
                    self.currentLineIndex -= 1

                elif ord(c) == 10: # enter
                    pass

                else: # any other character
                    s = s[:x] + c + s[x:]
                    self.currentLineIndex += 1
                    self.drawLines()

                self.fileLines[self.currentLine] = s

            if self.state == State.VISUAL:
                self.state = State.NORMAL

            if self.state == State.COMMAND_LINE:
                self.state = State.NORMAL

if __name__ == "__main__":
    editor = Editor()
    editor.run()
