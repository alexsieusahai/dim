import curses

def birth():
    curses.noecho()
    curses.cbreak()

def kill(editorObj):
    curses.echo()
    curses.nocbreak()
    editorObj.stdscr.keypad(False)
    curses.endwin()
