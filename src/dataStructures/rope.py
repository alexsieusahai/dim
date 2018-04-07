class Rope:

    def __init__(self, astr):
        self.length = len(astr)
        self.value = astr
        self.SPLIT_LENGTH = 8
        self.JOIN_LENGTH = 4

        self.left = None
        self.right = None

        self.adjust_tree()

    def adjust_tree(self):
        if self.value != '':
            if self.length > self.SPLIT_LENGTH:
                node_length = self.length // 2
                self.left = Rope(self.value[:node_length])
                self.right = Rope(self.value[node_length:])
                self.value = ''
            else:
                if self.length < self.JOIN_LENGTH:
                    self.value = str(self.left) + str(self.right)
                    self.left = None
                    self.right = None
    
    def __str__(self):
        """
        Get the string representation of the rope.
        """
        if hasattr(self, 'left') and hasattr(self,'right'):
            if self.left is None and self.right is None:
                return self.value
            return str(self.left) + str(self.right)

    def insert(self, position, value):
        """
        Insert a value at a specified position using properties of rope
        """
        if self.value != '':  # found a leaf
            self.value = self.value[:position] + value + self.value[position:]
        else:
            if position < self.left.length:
                self.left.insert(position, value)
                self.length = self.left.length + self.right.length
            else:
                self.right.insert(position - self.left.length, value)
        self.adjust_tree()

    def remove(self, start, end):
        """
        Removes indicies 
        start, start + 1, ... , end
        from string representation of rope
        """
        if self.value != '':  # found a leaf
            self.value = self.value[:start] + self.value[end:]
            self.length = len(self.value)
        else:
            left_start = min(start, self.left.length)
            left_end = min(end, self.left.length)
            right_start = max(0, min(start - self.left.length,
                                                    self.right.length))
            right_end = max(0, min(end - self.left.length, self.right.length))
            if left_start <= self.left.length:
                self.left.remove(left_start, left_end)

            if right_end > 0:
                self.right.remove(right_start, right_end)  # from tree property

            self.length = len(self.left.value) + len(self.right.value)

        self.adjust_tree()

if __name__ == "__main__":
    arope = Rope('brown fox jumped over a brown log')
    arope.insert(0, 'a ')
    arope.insert(1,' big')
    print(arope)
    arope.remove(1, 4)
    print(arope)
