import curses
from . import loadConfig

def initColors(SyntaxColors, Colors):
        """
        Initialize all colors and color pairs
        """
        curses.start_color()

        config = loadConfig.getColorConfig('Util/test.json')
        # get the general editor background, set to 0
        colorMap = {'BACKGROUND':0, 'STATUS_BACKGROUND':1}
        curses.init_color(0,
            config['BACKGROUND']['r'],
            config['BACKGROUND']['g'],
            config['BACKGROUND']['b']
            )
        curses.init_color(1,
            config['STATUS_BACKGROUND']['r'],
            config['STATUS_BACKGROUND']['g'],
            config['STATUS_BACKGROUND']['b']
            )
        i = 2
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
