def qsort(sortable_list):
	"""
	sorts a comparable list quickly
	worst case time complexity: O(n^2)

	can assume that average time complexity will be O(nlogn)
	objects must be comparable
	"""
	def recurse (i,j):
		"""
		i contains left bound of partition
		j contains right bound of partition
		pivotpoint determines where to pivot the list
		works best for completely randomized lists
		"""
		if i < j:
			pivotpoint = partition(i,j)
			recurse(i,pivotpoint-1)
			recurse(pivotpoint+1,j)

	def partition (i,j):
		"""
		gets the point at which to pivot the sortable
		creates two partitions with which to further sort

		in addition swaps values on the left and right as it moves through the partition
		this takes O(n) time, and partition gets called on average log n times
		"""
		first_value = sortable_list[i]

		left = i+1
		right = j

		while True:
			while left <= right and sortable_list[left] <= first_value:
				left += 1

			while sortable_list[right] >= first_value and right >= left:
				right -= 1

			if right < left:
				break

			else:
				sortable_list[left], sortable_list[right] = sortable_list[right],sortable_list[left]

		# swap the right and left values of the sortable list
		sortable_list[i], sortable_list[right] = sortable_list[right],sortable_list[i]

		return right

	# start the recursive sort
	recurse(0,len(sortable_list)-1)

def print_and_sort(l_to_sort):
	print('list before sorting: ', end='')
	print(l_to_sort)
	print('sorting...')
	print('list after sorting: ', end='')
	qsort(l_to_sort)
	print(l_to_sort)


if __name__ == "__main__":
	print_and_sort([1,6,3,4,2,1,34,21,19,1,-4,0,5,12])
	print_and_sort([-234234,1993,3,2,1,5,7,3,3,4,1,1,3,3,1,23,4,4,3 ])
	print_and_sort(['hello','my','name','is','amir','and','this','is','my','sorting','algorithm'])
