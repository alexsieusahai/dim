
# look into "wrapper" for debugging

from enum import Enum
import linecache

import curses


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

class Editor:

    def __init__(self):
        # handling curses
        self.stdscr = curses.initscr()
        self.editorscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, self.stdscr.getmaxyx()[1]-(MAX_LINE_NUMBER_LENGTH+1), 0, MAX_LINE_NUMBER_LENGTH+1)
        self.linenumscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, MAX_LINE_NUMBER_LENGTH+1, 0, 0)
        curses.noecho()
        curses.cbreak()
        curses.start_color() # have to make exceptions for terminals that don't support color
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # use as default for now

        # grabbing the lines from the file
        self.fileName = 'index.html'
        with open(self.fileName, 'r+') as f:
            self.fileLines = f.readlines()

        # make and store the savefile here

        (maxY,maxX) = self.stdscr.getmaxyx()

        # setting ui up
        self.editorscr.move(0,0)
        self.currentLine = 0
        self.currentLineIndex = 0
        self.topLine = 0
        self.drawLines()
        self.state = State.NORMAL


    def __exit__(self, exc_type, exc_value, traceback):
        """
        Prepares curses and filesystem for exit
        """
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()
        self.saveFile.close() # close the savefile

    def currentLineHeight(self):
        """
        Returns the height of the current line
        """
        return self.lineHeight(self.currentLine)

    def lineHeight(self, lineNumber):
        """
        Returns the height of line lineNumber
        """
        manyLines = len(self.fileLines[lineNumber])//(self.stdscr.getmaxyx()[1]-self.currentLineIndex)+1
        return manyLines if manyLines else 1


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
        topLine = self.topLine
        y = 0
        self.linenumscr.move(0,0)
        while y < self.linenumscr.getmaxyx()[0]-1:
            self.linenumscr.addstr(str(topLine+1))

            if topLine == self.currentLine:
                moveY = y + self.currentLineIndex//self.editorscr.getmaxyx()[1]
                moveX = self.currentLineIndex % self.editorscr.getmaxyx()[1]

            y += self.lineHeight(topLine)
            topLine += 1
            if y > self.linenumscr.getmaxyx()[0]-1:
                break
            self.linenumscr.move(y,0)



        # draw the lines themselves
        topLine = self.topLine
        self.editorscr.move(0,0)
        i = 0
        while True:
            if self.editorscr.getyx()[0]+self.lineHeight(self.topLine+i) > self.editorscr.getmaxyx()[0]-1: # handle unprintable text (no space at bottom) when scrolling up
                self.editorscr.addstr('@')
                break
            for c in self.fileLines[topLine+i]:
                self.editorscr.addstr(c)
                if self.editorscr.getyx()[1]+1 > self.editorscr.getmaxyx()[1]-1:
                    self.editorscr.move(i+1,0)
            if self.editorscr.getyx()[0] + 1 > self.editorscr.getmaxyx()[0]-1:
                break
            self.editorscr.move(i+1,0)
            i += 1

        # move cursor to where it should be as specified by currentLine and currentLineIndex, refresh and move on
        self.editorscr.move(moveY,moveX)
        self.linenumscr.refresh()
        self.editorscr.refresh()
        pass

    def moveDown(self,y,x):
        """
        Moves down one line
        """
        if y+self.lineHeight(self.currentLine)-1 < self.editorscr.getmaxyx()[0]-2:
            self.editorscr.move(y+self.currentLineHeight(),x)
            self.currentLine += 1
        elif len(self.fileLines)-self.currentLine > 0:
            self.currentLine += 1
            self.topLine += self.lineHeight(self.currentLine)

    def moveUp(self,y,x):
        if y > 0:
            self.editorscr.move(y-self.lineHeight(self.currentLine-1),x)
            self.currentLine -= 1
        elif self.currentLine > 0:
            self.currentLine -= 1
            self.topLine -= 1

    def moveLeft(self,y,x):
        if x > 0:
            self.editorscr.move(y,x-1)
            self.currentLineIndex -= 1

    def moveRight(self,y,x):
        if x < self.editorscr.getmaxyx()[1]-1:
            self.editorscr.move(y,x+1)
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
                if c == 'k': # up
                    self.moveUp(y,x)
                if c == 'h': # left
                    self.moveLeft(y,x)
                if c == 'l': # right
                    self.moveRight(y,x)

                # jumping movement
                if c == 'w': # jump to char before last space from left to right, after current char
                    x += 1
                    lineInd = x
                    if self.fileLines[self.currentLine] == '\n':
                        self.currentLine += 1
                        self.editorscr.move(y+1,x-1)
                        continue

                    while self.fileLines[self.currentLine][lineInd] != ' ':
                        x += 1
                        self.currentLineIndex += 1
                        if x >= self.editorscr.getmaxyx()[1]-1:
                            y += 1
                            x = 0
                            lineInd += 1
                        if x >= len(self.fileLines[self.currentLine]):
                            x = 0
                            y += 1
                            lineInd = 0
                            self.moveDown(y,x)
                    while self.fileLines[self.currentLine][lineInd] == ' ':
                        x += 1
                        lineInd += 1
                        if x >= len(self.fileLines[self.currentLine]):
                            x = 0
                            y += 1
                            lineInd = 0
                            self.moveDown(y,x)

                    self.editorscr.move(y,x)
                    pass
                if c == 'b': # jump to char before last space from right to left, after current char
                    pass

                # move to different states
                if c == 'i':
                    self.state = State.INSERT
                if c == 'v':
                    self.state = State.VISUAL
                if c == ':':
                    self.state = State.COMMAND_LINE

            if self.state == State.INSERT:
                c = chr(self.editorscr.getch())

                if ord(c) == 27:
                    self.state = State.NORMAL
                else:
                    s = self.fileLines[self.currentLine]
                    s = s[:x] + c + s[x:]
                    self.fileLines[self.currentLine] = s
                    self.editorscr.move(y,x+1)

            if self.state == State.VISUAL:
                self.state = State.NORMAL

            if self.state == State.COMMAND_LINE:
                self.state = State.NORMAL

if __name__ == "__main__":
    editor = Editor()
    editor.run()
