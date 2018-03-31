from dataStructures.lineNode import LineNode

class LineLinkedList: # doubly linked list for storing lines
    def __init__(self,lineList):
        """
        Constructs a doubly linked list of lineNodes with the following attributes:
        start (the node at the top)
        end (the node at the bottom)
        length (the length of the object)
        """
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
        """
        print linked list as list
        """

        LL_as_list = self.toList()
        print(' '.join(LL_as_list))

if __name__ == '__main__':
    ll = LineLinkedList([x for x in 'dog'])
    walkNode = ll.start
    while walkNode.nextNode != None:
        print(walkNode.value)
        walkNode = walkNode.nextNode
    print(walkNode.value)
