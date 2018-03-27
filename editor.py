
class Editor:
    def __init__(self,cursesscr,currentLine):
        self.currentLine = self.topLine = currentLine
        self.currentLineCount = 0
        self.currentLineIndex = 0
        self.scr = cursesscr
        self.lineLinkedList = None

