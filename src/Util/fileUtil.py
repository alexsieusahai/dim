from dataStructures.lineLinkedList import LineLinkedList

def loadFile(fileName):
    """
    Loads all lines from the fileName in cwd
    Returns a LineLinkedList object
    """
    with open(fileName, 'r') as f:
        fileLines = f.readlines()
    # making the linked list
    return(LineLinkedList(fileLines))

def saveFile(editorObj):
    """
    Saves all lines in lineLinkedList to the file with the name editorObj.fileName in cwd
    """
    f = open(editorObj.fileName, 'w')
    walk = editorObj.lineLinkedList.start
    while walk != None:
        f.write(walk.value)
        walk = walk.nextNode
