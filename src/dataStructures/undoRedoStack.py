from dataStructures.lineNode import LineNode
import Util.editorUtil as editorUtil

class UndoRedoStack:
    """
    This object handles all of the undoing the redoing
    and does the appropriate actions to the editorObj.
    """
    def __init__(self):
        self.undoStack = []
        self.redoStack = []

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
        """
        Helper function for undo and redo.

        Get the current line value and the current index at a line
        and return it for other use.
        """
        currentValue = linePointer.value
        currentIndex = editorObj.currentLineIndex
        return ((linePointer, currentValue, currentIndex))

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

        # case
        elif isinstance(action[0], str):
            if action[0] == 'delete':
                line = action[1].lastNode
                line.value = action[2]
                editorUtil.deleteLine(editorObj, action[1], trueDelete=True)
                lineIndex = len(line.value)-2
                line.colors = []
                for c in line.value:
                    line.colors.append(0)
            if action[0] == 'insert':
                line = action[1]
                line.value = action[3]
                line.colors = []
                for c in line.value:
                    line.colors.append(0)
                lineIndex = 0
                editorUtil.insertLine(editorObj, action[1], cleanInsert=True)
                line.nextNode.value = action[2]
                line.nextNode.colors = []
                for c in line.nextNode.value:
                    line.nextNode.colors.append(0)

        editorObj.moveToNode(line, lineIndex)

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
        if isinstance(action[0], LineNode):
            self.redoStack.append(self.getCurrentState(editorObj, action[0]))
        elif isinstance(action[0], str):
            if action[0] == 'delete':
                self.redoStack.append(('insert', action[1].lastNode,
                                    action[1].value, action[1].lastNode.value))
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
        if isinstance(action[0], LineNode):
            self.undoStack.append(self.getCurrentState(editorObj, action[0]))
        elif isinstance(action[0], str):
            if action[0] == 'insert':
                self.undoStack.append(['delete', action[1].nextNode, ''])
        self.doAction(action, editorObj)
