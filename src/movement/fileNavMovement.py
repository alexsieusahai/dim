import Util.editorUtil as editorUtil

def moveDown(fileNavObj, y):
    """
    Move down one step
    """
    y += editorUtil.lineHeight(fileNavObj.filenavscr, fileNavObj.currentDir)

    if fileNavObj.currentDir.nextNode is None:
        # if we are at the end
        y -= editorUtil.lineHeight(fileNavObj.filenavscr, fileNavObj.currentDir)

    if y > fileNavObj.filenavscr.getmaxyx()[0]-2:
        y -= editorUtil.lineHeight(fileNavObj.filenavscr, fileNavObj.currentDir)
        fileNavObj.topDir = fileNavObj.topDir.nextNode

    if fileNavObj.currentDir is not fileNavObj.dirs.end:
        fileNavObj.currentDir = fileNavObj.currentDir.nextNode

    return y

def moveUp(fileNavObj, y):
    """
    Move up one step
    """
    y -= editorUtil.lineHeight(fileNavObj.filenavscr, fileNavObj.currentDir.lastNode)
    # remember you have ' -' at the start of every dir
    if y < 0:
        temp = fileNavObj.topDir
        fileNavObj.topDir = fileNavObj.topDir.lastNode
        if fileNavObj.topDir is None:
            fileNavObj.topDir = temp
            fileNavObj.currentDir = fileNavObj.currentDir.nextNode
        y += editorUtil.lineHeight(fileNavObj.filenavscr, fileNavObj.currentDir.lastNode)
    if fileNavObj.currentDir is not fileNavObj.dirs.start:
        fileNavObj.currentDir = fileNavObj.currentDir.lastNode
    return y
