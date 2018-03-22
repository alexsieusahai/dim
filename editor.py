
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
        self.editorscr = curses.newwin(self.stdscr.getmaxyx()[0], self.stdscr.getmaxyx()[1]-4, 0, 4)
        self.linenumscr = curses.newwin(self.stdscr.getmaxyx()[0], 4, 0, 0)
        curses.noecho()
        curses.cbreak()
        curses.start_color() # have to make exceptions for terminals that don't support color
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # use as default for now

        
        # grabbing all the lines initially, don't want to grab them all with file; only keep what you need in memory
        self.fileName = 'a.cpp'
        self.lines = []
        (maxY,maxX) = self.stdscr.getmaxyx()
        maxLines = maxY
        i = 0
        while maxLines:
            self.lines.append(linecache.getline(self.fileName, i))
            lineLength = len(self.lines[-1])//maxX
            if not lineLength: lineLength = 1 # meaning nothing on line
            maxLines -= lineLength
            i += 1
        for line in self.lines:
            try:
                self.editorscr.addstr(line+'\n')
            except:
                break

        # set up the swap file
            

        # setting ui up
        self.editorscr.move(0,0)
        self.currentLine = 0
        self.drawLineNumbers(0)
        self.state = State.NORMAL
            

    def __exit__(self, exc_type, exc_value, traceback):
        #handling curses
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()


    def currentLineHeight(self):
        return self.lineHeight(self.currentLine)

    def lineHeight(self, lineNumber):
        return 1

    def drawLineNumbers(self,topLine):
        (oldy,oldx) = self.editorscr.getyx()
        y = 0
        self.linenumscr.move(0,0)
        for line in self.lines:
            self.linenumscr.addstr(str(topLine+1))
            y += 1
            topLine += 1
            self.linenumscr.move(y,0)
        self.linenumscr.refresh()
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
                if c == 'k': # up
                    if y > 0:
                        self.editorscr.move(y-self.currentLineHeight(),x)
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
