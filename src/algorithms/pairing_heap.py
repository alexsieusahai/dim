class PairingHeap:
	"""
	Same functionality as binary heap but faster insert and merge

	insert O(1)			O(log n) for binary heap
	remove O(n) for 1 operation, O(log n) over many
	get minimum O(1)
	remove minimum O(n) for 1 operation, O(log n) over many  
	merge O(1) for 1 operation, O(log n) over many

	generally performs better than a binary heap
	"""

	def __init__(self):
		"""
		creates pairing heap
		"""

		self.r = None

	def __len__(self):

		# if the heap is empty
		if self.r == None:
			return 0

		# if heap is not empty
		else:
			return 1


	def min(self):
		"""
		gets whatever is at the top of the heap
		should be the minimum
		"""

		if self.r == None:
			raise IndexError("the heap is empty")

		return (self.r.key, self.r.val)

	def popmin(self):

		minval = self.min()

		# fixing the pairing heap
		self.r = self._pairmerge(self.r.children)
		return minval


	def _merge(self, n1, n2):
		"""
		merges heaps of nodes n1 and n2
		very fast, O(1) time
		"""
		if n1 == None:
			return n2

		if n2 == None:
			return n1

		if n1.val < n2.val:
			n1.children.append(n2)
			return n1

		else:
			n2.children.append(n1)
			return n2


	def insert(self, key, val):
		"""
		inserts into heap with item and key
		"""
		n = HeapNode(key, val)
		self.r = self._merge(self.r, n)
		print(self.r.key, "huh", self.r.val)


	def _pairmerge(self, pairs):
		"""
		length will determine how to merge pairs
		"""
		length = len(pairs)
		
		# edge case
		if length == 0:
			return None

		# recursion base case
		if length == 1:
			return pairs[0]

		# recursion merges the rest of the pairs
		return self._merge(self._merge(pairs[0], pairs[1]), self._pairmerge(pairs[2:]))


class HeapNode:
	"""
	creates node in the pairing heap
	each node has a value and children
	if children length is 0 it is a leaf node
	"""

	def __init__(self, key, val):
		"""
		creates node of pairing heap
		"""
		self.val = val
		self.key = key
		self.children = []

	def is_leaf(self):
		"""
		return True if has no children
		otherwise return False
		"""

		return len(self.children) == 0

def heapsort(items):
    """
    Returns the sorted list of items.

    >>> heapsort([5,4,2,1,2,3])
    [1, 2, 2, 3, 4, 5]
    >>> heapsort([1])
    [1]
    >>> heapsort([])
    []
    """

    heap = PairingHeap()
    for x in items:
        heap.insert(None, x)
    sorted = []
    while heap:
        sorted.append(heap.popmin()[1])
    return sorted

if __name__ == "__main__":

	print(heapsort([5,4,2,1,2,3]))