from dataStructures.lineNode import LineNode

class UndoRedoStack:
    """
    This object handles all of the undoing the redoing
    and does the appropriate actions to the editorObj.
    """
    def __init__(self):
        self.undoStack = []
        self.redoStack = []

    def doAction(self, action, editorObj):
        """
        Helper function for undo and redo;
        does the action supplied to editorObj.
        """
        # case 1; tuple that looks like
        # (lineNode, lineNode.value)
        if isinstance(action[0], LineNode):
            # if we are operating on a lineNode
            action[0].value = action[1]
            lineIndex = action[2]
            line = action[0]
        # move to that place
        editorObj.moveToNode(line, lineIndex)

    def pushOntoUndo(self, action):
        """
        Pushes an action onto the undo stack.
        Called whenever an action is completed.
        """
        self.undoStack.append(action)

    def pushOntoRedo(self, action):
        """
        Pushes an action onto the redo stack.
        Called whenever you want to save an action
        to redo.
        """
        self.redoStack.append(action)

    def getCurrentState(self, editorObj, linePointer):
        currentValue = linePointer.value
        currentIndex = editorObj.currentLineIndex
        return ((linePointer, currentValue, currentIndex))


    def undo(self, editorObj):
        """
        undoStack has the actions that editorObj
        has executed and kept saved.

        Does the inverse of the last action to
        editorObj, then puts the action onto the redo stack
        """
        if len(self.undoStack) == 0:
            return  # nothing to undo
        action = self.undoStack.pop()
        self.redoStack.append(self.getCurrentState(editorObj, action[0]))
        self.doAction(action, editorObj)

    def redo(self, editorObj):
        """
        redoStack has the actions that undo has put
        onto the redoStack.

        Does the last action on redo stack, pops it off
        the redo stack and puts the inverse of that action into
        the undo stack.
        """
        if len(self.redoStack) == 0:
            return  # nothing to redo
        action = self.redoStack.pop()
        self.undoStack.append(self.getCurrentState(editorObj, action[0]))
        self.doAction(action, editorObj)
