from dataStructures.lineNode import LineNode

class LineLinkedList: # doubly linked list for storing lines
    def __init__(self,lineList):
        self.length = 0
        self.start = None
        self.end = None
        lastNode = None
        for line in lineList:
            node = LineNode(line,lastNode)

            if self.start == None:
                self.start = node

            node.lastNode = lastNode
            if lastNode != None:
                lastNode.nextNode = node
            lastNode = node
            self.length += 1
        self.end = lastNode

    def toList(self):
        """
        takes its own linked list and constructs a list based off of it
        """
        walk = self.start
        alist = []

        while walk is not None:
            alist.append(walk.value)
            walk = walk.nextNode

        return alist

    def print_LL(self):

        LL_as_list = self.toList()
        print(LL_as_list)

if __name__ == '__main__':
    ll = LineLinkedList([x for x in 'dog'])
    walkNode = ll.start
    while walkNode.nextNode != None:
        print(walkNode.value)
        walkNode = walkNode.nextNode
    print(walkNode.value)
