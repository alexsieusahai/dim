import BurrowsWheelerTransform as bw

def transform_stream(filestream):
	"""
	takes filestream input and performs a burrows wheeler transform on it
	creates another filestream for output.3
	"""

	s = filestream.read()
	I, L = bw.burrowsWheeler(s)
	return I, L


def save_compressed(filename):
	"""
	takes file name
	performs burrows wheeler transform
	compresses the data
	writes compressed data to file
	"""

	with open(filename, 'r') as untransformed:
		I, L = transform_stream(untransformed)

	with open(filename, 'w') as towrite:
		f.write(str(I))
		f.write(" ")
		f.write(L)

	with open(filename, 'a') as tocompress:
		freqs = huffman.make_freq_table(tocompress)
		tree = huffman.make_tree(freqs)
		tocompress.seek(0)
		with open(filename+'.huf', 'wb') as compressed:
		    util.compress(tree, tocompress, compressed)

def open_decompressed(filename):

	with open(path+'.huf', 'rb') as compressed:
		with open(path, 'w') as decompressed:
        	util.decompress(compressed, decompressed)

    """
    TODO read from filename, get the first number, then get the rest

    untransform it using BW

    then write it back to a file
    """

	with open(filename, 'r') as f:
        fileLines = f.readlines()
    if fileLines:
        # making the linked list
        return LineLinkedList(fileLines)
    return LineLinkedList(['\n'])



if __name__ == "__main__":
	with open('temp', 'r') as untransformed:
		transform_stream(untransformed)