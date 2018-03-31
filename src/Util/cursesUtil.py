import curses

def birth():
    """
    Set up curses for dim
    """
    curses.noecho()
    curses.cbreak()

def kill(editorObj):
    """
    End curses stuff so the terminal isn't left
    cripped by running dim
    """
    curses.echo()
    curses.nocbreak()
    editorObj.stdscr.keypad(False)
    curses.endwin()
