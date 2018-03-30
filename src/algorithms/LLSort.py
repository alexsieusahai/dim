def LLSort(sortable_LL):
	"""
	Takes a linked list as input and sorts it
	O(nlogn) complexity

	input: LineLinkedList unsorted
	returns: LineLinkedList sorted
	"""

	def middle_node (head):
		"""
		traverse the linked list with 2 pointers: front and back
		front moves twice as fast as back. When front reaches the end of the
		linked list, back will be at the middle.

		return tnhe node at the back
		"""
		if head == None:
			return head

		front = head.nextNode
		back = head

		while front != None:
			front = front.nextNode
			if front != None:
				front = front.nextNode
				back = back.nextNode
		return back # this will now be the middle of the linked list

	def merge(nodeA, nodeB):
		"""
		takes two halves of a linked list and merges them
		each half is sorted
		"""
		
		# base case 1 of the recursion
		if nodeA == None:
			return nodeB

		# base case 2 of the recursion
		elif nodeB == None:
			return nodeA

		if nodeA.value <= nodeB.value:
			merged = nodeA
			merged.nextNode = merge(nodeA.nextNode,nodeB)
			merged.nextNode.lastNode = merged

		else:
			merged = nodeB
			merged.nextNode = merge(nodeA,nodeB.nextNode)
			merged.nextNode.lastNode = merged

		return merged

	def recurse(head):

		if head == None or head.nextNode == None:
			return head

		mid1 = middle_node(head)

		"""
		mid2 contains the head of the other half of the linked list
		this is because we will override it from mid1 to create a psuedo
		two separate lists for doing the merge sort.
		"""
		mid2 = mid1.nextNode

		mid1.nextNode = None

		left_half = recurse(head)
		right_half = recurse(mid2)

		return merge(left_half,right_half)

	def fix_previous_pointers(head):
		"""
		sorting algorithms ensures that each nextNode.value will be larger than the 
		current node.value

		the previous pointers do not have the same guarentee (same as the unsorted list)
		this method fixes all of the previous pointers
		"""

		if head == None:
			return head

		pointer_node = head

		while pointer_node.nextNode != None:
			pointer_node.nextNode.lastNode = pointer_node
			pointer_node = pointer_node.nextNode

		return head



	sorted_head = recurse(sortable_LL.start)
	sortable_LL.remake_list(sorted_head)

if __name__ == "__main__":
	"""
	add tests here and stuff

	import linked list object
	"""
	pass