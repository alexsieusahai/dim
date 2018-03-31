from dataStructures.lineNode import LineNode

class LineLinkedList:
    """
    doubly linked list created with lineNode objects

    each value contains a string (could contain other objects)
    constructor takes in a list of values, usually strings, to creat the
    linked list
    """

    def __init__(self,lineList):
        """
        lineList is a list object containing either objects
        generally should be strings
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

    def remake_list(self,headNode):
        """
        taking a head node, remakes the linked list object using it
        """

        # set our start to the new head node
        self.start = headNode
        self.length = 0
        pointer_node = headNode

        # go through the linked list from the head node
        # thi is to get the size of the list, as well as find the very last list
        while pointer_node != None:
            pointer_node = pointer_node.nextNode
            self.length += 1

        self.end = pointer_node

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
