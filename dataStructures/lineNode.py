class LineNode:

    def __init__(self,line,lastNode):
        self.value = line
        self.colors = []
        for c in line:
            self.colors.append(0) # set all colors to default color scheme, which will be 0
        self.lastNode = lastNode
        self.nextNode = None

