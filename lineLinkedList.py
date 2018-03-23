from lineNode import LineNode

class lineLinkedList: # doubly linked list for storing lines
    def __init__(self,lineList):
        self.length = 0
        self.start = None
        self.end = None
        lastNode = None
        for line in lineList:
            node = LineNode(self.length,line,lastNode)

            if self.start == None:
                self.start = node

            node.lastNode = lastNode
            if lastNode != None:
                lastNode.nextNode = node
            lastNode = node
            self.length += 1
        self.end = lastNode

if __name__ == '__main__':
    ll = lineLinkedList([x for x in 'dog'])
    walkNode = ll.start
    while walkNode.nextNode != None:
        print(walkNode.value+' '+str(walkNode.index))
        walkNode = walkNode.nextNode
    print(walkNode.value+' '+str(walkNode.index))
