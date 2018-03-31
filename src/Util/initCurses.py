import os

import curses
from . import loadConfig

def initColors(dimDir, fileName):
        """
        Initialize all colors and color pairs
        """
        curses.start_color()

        temp = os.getcwd()  # save it for later so we can go back
        os.chdir(dimDir)

        config = loadConfig.getColorConfig('themes/'+fileName)
        # get the general editor background, set to 0
        colorMap = {'BACKGROUND':10, 'STATUS_BACKGROUND':11}
        curses.init_color(10,
            config['BACKGROUND']['r'],
            config['BACKGROUND']['g'],
            config['BACKGROUND']['b']
            )
        curses.init_color(11,
            config['STATUS_BACKGROUND']['r'],
            config['STATUS_BACKGROUND']['g'],
            config['STATUS_BACKGROUND']['b']
            )
        i = 12
        for typeSyntax in config:
            if (typeSyntax == 'BACKGROUND' or
                    typeSyntax == 'STATUS_BACKGROUND'):
                continue
            if typeSyntax == 'STATUS':
                curses.init_color(i,
                        config[typeSyntax]['r'],
                        config[typeSyntax]['g'],
                        config[typeSyntax]['b']
                        )
                curses.init_pair(i,
                        i,
                        colorMap['STATUS_BACKGROUND']
                        )
            else:
                curses.init_color(i,
                        config[typeSyntax]['r'],
                        config[typeSyntax]['g'],
                        config[typeSyntax]['b']
                        )
                curses.init_pair(i,
                        i,
                        colorMap['BACKGROUND']
                        )

            colorMap[typeSyntax] = i
            i += 1

        os.chdir(temp)  # go back to where you were before
        return colorMap

def initScreens(editorObj,Constants):
        """
        This function initializes all the screens to be painted on
        """

        editorObj.stdscr = curses.initscr()
        editorObj.editorscr = curses.newwin(
                editorObj.stdscr.getmaxyx()[0]-2,
                editorObj.stdscr.getmaxyx()[1]-(Constants.MAX_LINE_NUMBER_LENGTH.value+1)-Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value,
                0,
                Constants.MAX_LINE_NUMBER_LENGTH.value+1+Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value)

        editorObj.linenumscr = curses.newwin(
                editorObj.stdscr.getmaxyx()[0]-2,
                Constants.MAX_LINE_NUMBER_LENGTH.value+1,
                0,
                Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value)

        editorObj.filenavscr = curses.newwin(
                editorObj.stdscr.getmaxyx()[0],
                Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value,
                0,
                0)

        editorObj.statusscr = curses.newwin(
                1,
                editorObj.stdscr.getmaxyx()[1]-Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value,
                editorObj.stdscr.getmaxyx()[0]-2,
                Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value)

        editorObj.cmdlinescr = curses.newwin(
                1,
                editorObj.stdscr.getmaxyx()[1]-Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value,
                editorObj.stdscr.getmaxyx()[0]-1,
                Constants.FILE_SUBSYSTEM_WINDOW_LENGTH.value)
