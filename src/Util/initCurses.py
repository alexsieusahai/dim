import curses

def initColors(SyntaxColors, Colors):
        """
        Initialize all colors and color pairs
        """
        curses.start_color()
        curses.init_color(Colors.COOL_GREY.value, 125, 150, 175)
        curses.init_color(Colors.MEDIUM_GREY.value, 400, 400, 400)
        curses.init_color(Colors.LIGHT_GREY.value, 700, 700, 700)
        curses.init_color(Colors.WHITE.value, 1000, 1000, 1000)
        curses.init_color(Colors.BLACK.value, 0, 0, 0)
        curses.init_color(Colors.YELLOW.value, 1000, 1000, 0)
        curses.init_color(Colors.BLUE.value, 0, 0, 1000)
        curses.init_color(Colors.FUCHSIA.value, 1000, 0, 500)
        curses.init_color(Colors.PURPLE.value, 600, 200, 900)
        curses.init_color(Colors.BROWN.value, 750, 200, 70)
        curses.init_color(Colors.ORANGE.value, 1000, 350, 0)
        curses.init_color(Colors.LIME_GREEN.value, 0, 1000, 500)
        curses.init_color(Colors.TURQUOISE.value, 150, 1000, 700)
        curses.init_color(Colors.CYAN.value, 0, 1000, 1000)
        curses.init_color(Colors.PASTEL_RED.value, 1000, 410, 380)

        # handle colors for syntax highlighting
        curses.init_pair(SyntaxColors.TEXT.value, Colors.WHITE.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.LINE_NUMBER.value, Colors.MEDIUM_GREY.value, Colors.COOL_GREY.value) # lighter grey text, cool grey background
        curses.init_pair(SyntaxColors.STATUS.value, Colors.BLACK.value, Colors.WHITE.value)
        curses.init_pair(SyntaxColors.COMMENT.value, Colors.LIGHT_GREY.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.NAMESPACE.value, Colors.LIME_GREEN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.KEYWORD.value, Colors.ORANGE.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.BUILTIN.value, Colors.CYAN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.FUNCTION.value, Colors.LIME_GREEN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.LITERAL.value, Colors.PASTEL_RED.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.OPERATOR.value, Colors.YELLOW.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.STRING_LITERAL.value, Colors.BROWN.value, Colors.COOL_GREY.value)

        # file nav pairs
        curses.init_pair(SyntaxColors.FILE.value, Colors.LIGHT_GREY.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.FOLDER.value, Colors.CYAN.value, Colors.COOL_GREY.value)
        curses.init_pair(SyntaxColors.EXECUTABLE.value, Colors.LIME_GREEN.value, Colors.COOL_GREY.value)

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
