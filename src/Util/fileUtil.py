from dataStructures.lineLinkedList import LineLinkedList

def loadFile(fileName):
    """
    Loads all lines from the fileName in cwd
    Returns a LineLinkedList object

    If file fileName is empty, 
    returns a LineLinkedList object with just one newline node
    """
    with open(fileName, 'r') as f:
        fileLines = f.readlines()
    if fileLines:
        # making the linked list
        return LineLinkedList(fileLines)
    return LineLinkedList(['\n'])

def saveFile(editorObj):
    """
    Saves all lines in lineLinkedList to the file with the name editorObj.fileName in cwd
    """
    f = open(editorObj.fileName, 'w')
    walk = editorObj.lineLinkedList.start
    while walk != None:
        f.write(walk.value)
        walk = walk.nextNode
