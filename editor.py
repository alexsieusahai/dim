
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



class Editor:

    def __init__(self):
        # handling curses
        self.stdscr = curses.initscr()
        self.editorscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, self.stdscr.getmaxyx()[1]-4, 0, 4)
        self.linenumscr = curses.newwin(self.stdscr.getmaxyx()[0]-2, 4, 0, 0)
        curses.noecho()
        curses.cbreak()
        curses.start_color() # have to make exceptions for terminals that don't support color
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # use as default for now

        # grabbing the lines from the file
        self.fileName = 'a.cpp'
        with open(self.fileName, 'r+') as f:
            self.fileLines = f.readlines()
            
        # make and store the savefile here

        (maxY,maxX) = self.stdscr.getmaxyx()
        for line in self.fileLines:
            try:
                self.editorscr.addstr(line)
            except:
                break


        # setting ui up
        self.editorscr.move(0,0)
        self.currentLine = 0
        self.drawLines()
        self.state = State.NORMAL
            

    def __exit__(self, exc_type, exc_value, traceback):
        #handling curses
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()
        self.saveFile.close() # close the savefile

    def currentLineHeight(self):
        return self.lineHeight(self.currentLine)

    def lineHeight(self, lineNumber):
        manyLines = len(self.fileLines[lineNumber])//self.stdscr.getmaxyx()[1]+1
        return manyLines if manyLines else 1


    def drawLines(self):
        (oldy,oldx) = self.editorscr.getyx()

        # draw lines
        topLine = self.currentLine-oldy
        y = 0
        self.linenumscr.move(0,0)
        for line in self.fileLines:
            self.linenumscr.addstr(str(topLine+1))
            increm = self.lineHeight(topLine)
            y += increm
            topLine += 1 
            self.linenumscr.move(y,0)
            if y > self.linenumscr.getmaxyx()[0]-2:
                self.linenumscr.addstr(str(topLine+1))
                break
        
        self.editorscr.move(0,0)
        for i in range(self.editorscr.getmaxyx()[0]):
            try:
                self.editorscr.addstr(self.fileLines[topLine+i])
            except: 
                a = 1

        self.linenumscr.refresh()
        self.editorscr.refresh()
        self.editorscr.move(oldy,oldx)
        pass

    def run(self):
        while True:
            (y,x) = self.editorscr.getyx() # get cursor position relative to top left
            if self.state == State.NORMAL:
                c = chr(self.editorscr.getch()) #get a key

                # movement
                # remember top left is (0,0)
                if c == 'j': # down
                    if y < self.editorscr.getmaxyx()[0]-1:
                        self.editorscr.move(y+self.currentLineHeight(),x)
                        self.currentLine += 1
                    elif len(self.fileLines)-self.currentLine > 0:
                        self.currentLine += 1
                        self.drawLines()
                if c == 'k': # up
                    if y > 0:
                        self.editorscr.move(y-self.currentLineHeight(),x)
                        self.currentLine -= 1
                if c == 'h': # left 
                    if x > 0:
                        self.editorscr.move(y,x-1)
                if c == 'l': # right
                    if x < self.editorscr.getmaxyx()[1]-1:
                        self.editorscr.move(y,x+1)

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
                    self.editorscr.addstr(c)

            if self.state == State.VISUAL:
                self.state = State.NORMAL

            if self.state == State.COMMAND_LINE:
                self.state = State.NORMAL

if __name__ == "__main__":
    editor = Editor()
    editor.run()
