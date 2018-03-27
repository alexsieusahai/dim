from enum import Enum

class State(Enum):
    NORMAL = 0
    INSERT = 1
    VISUAL = 2
    COMMAND_LINE = 3
    FILE_NAVIGATION = 4

class NormalState(Enum):
    MOVEMENT = 0
    DELETE = 1
    # what else do I need

class SyntaxColors(Enum):

    # file nav stuff
    FILE = 1
    FOLDER = 2
    EXECUTABLE = 3

    # editor (syntax highlighting) stuff
    TEXT = 20
    CONSTANT = 21
    DECLARATION = 22
    NAMESPACE = 23
    TYPE = 24
    NAME = 25
    FUNCTION = 26
    STRING_LITERAL = 27
    LITERAL = 28
    OPERATOR = 29
    COMMENT = 30
    LINE_NUMBER = 31
    STATUS = 32
    KEYWORD = 33
    BUILTIN = 34

class Colors(Enum):

    MEDIUM_GREY = 10
    WHITE = 11
    COOL_GREY = 12
    BLACK = 13
    YELLOW = 15
    BLUE = 14
    FUCHSIA = 16
    PURPLE = 17
    BROWN = 18
    ORANGE = 19
    LIME_GREEN = 20
    TURQUOISE = 21
    CYAN = 22
    LIGHT_GREY = 23
    PASTEL_RED = 24

class WindowConstants(Enum):
    MAX_LINE_NUMBER_LENGTH = 4
    FILE_SUBSYSTEM_WINDOW_LENGTH = 18
