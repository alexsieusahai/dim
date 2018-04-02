from dataStructures.lineLinkedList import LineLinkedList
from dataStructures.lineNode import LineNode

# best solution isn't implemented yet; haven't figured out how to deal with
# deleting lines; maybe a really nice solution exists but this will work fine 
# unless the file is thousands of lines long

class UndoRedoStack:
    """
    This object handles all of the undoing the redoing
    and does the appropriate actions to the editorObj.
    """
    def __init__(self):
        self.undoStack = []
        self.redoStack = []

    def add(beforeNode, afterNode, betweenLinkedList):
        """
        Add in the betweenLinkedList to beforeNode and afterNode
        like this:
        ... <-> beforeNode <->  afterNode <-> ...
        To
        ... <-> beforeNode <-> btwLL.start <-> ... <-> btwLL.end <-> afterNode <-> ...
        """
        beforeNode.nextNode = betweenLinkedList.start
        betweenLinkedList.start.lastNode = beforeNode
        betweenLinkedList.end.nextNode = afterNode
        afterNode.lastNode = betweenLinkedList.end

    def remove(beforeNode, afterNode):
        """
        Remove all of the data in between beforeNode and afterNode
        Don't have to garbage collect since python will handle it for me?
        ... <-> beforeNode <-> code in between <-> afterNode <-> ...
        To
        ... <-> beforeNode <-> afterNode <-> ...
        """
        beforeNode.nextNode = afterNode
        afterNode.lastNode = beforeNode

    def pushOntoUndo(self, editorObj):
        """
        copy the linked list, and store it on the undo stack
        stores a tuple of (linkedlist, currentline, topline)
        """
        self.undoStack.append(copy(editorObj))

    def pushOntoRedo(self, editorObj):
        """
        copy the linked list, and store it on the redo stack
        stores a tuple of (linkedlist, currentline, topline)
        """
        self.redoStack.append(copy(editorObj))

    def undo(self, editorObj):
        """
        Pop undoStack and keep it as alist
        Push the current lineLinkedList onto redo
        Make alist editorObj.lineLinkedList
        uses a tuple of (linkedlist, currentline, topline)
        """
        if len(self.undoStack) == 0:
            return
        (alist, curline, topline) = self.undoStack.pop()
        self.pushOntoRedo(editorObj)
        editorObj.lineLinkedList = alist
        editorObj.currentLine = curline
        editorObj.topLine = topline

    def redo(self, editorObj):
        """
        Pop redoStack and keep it as alist
        Push the current lineLinkedList onto undo
        Make alist editorObj.lineLinkedList
        uses a tuple of (linkedlist, currentline, topline)
        """
        if len(self.redoStack) == 0:
            return
        (alist, curline, topline) = self.redoStack.pop()
        self.pushOntoUndo(editorObj)
        editorObj.lineLinkedList = alist
        editorObj.currentLine = curline
        editorObj.topLine = topline

def copy(editorObj):
    """
    Copy aLinkedList and return a pointer to it
    """
    currentLine = topLine = None
    walk = editorObj.lineLinkedList.start
    newList = LineLinkedList([])
    lastNode = None
    while walk != None:
        node = LineNode(walk.value, None)
        if node.value == editorObj.topLine.value:
            topLine = node

        if node.value == editorObj.currentLine.value:
            currentLine = node
        if newList.start is None:
             newList.start = node
        node.lastNode = lastNode
        if lastNode != None:
            lastNode.nextNode = node
        lastNode = node
        newList.length += 1

        walk = walk.nextNode
        if walk is None:
            break

    newList.end = lastNode
    if currentLine is None:
        currentLine = newList.start
    if topLine is None:
        topLine = newList.start
    return (newList, currentLine, topLine)
