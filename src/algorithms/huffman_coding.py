import bitio
import huffman


def read_tree(bitreader):
    '''Read a description of a Huffman tree from the given bit reader,
    and construct and return the tree. When this function returns, the
    bit reader should be ready to read the next bit immediately
    following the tree description.

    Huffman trees are stored in the following format:
      * TreeLeaf is represented by the two bits 01, followed by 8 bits
          for the symbol at that leaf.
      * TreeLeaf that is None (the special "end of message" character) 
          is represented by the two bits 00.
      * TreeBranch is represented by the single bit 1, followed by a
          description of the left subtree and then the right subtree.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.

    Returns:
      A Huffman tree constructed according to the given description.
    '''

    def read_prefix ():
        '''
        1  - go to read_treeBranch()
        01 - go to read_treeLeaf()
        00 - go to read_end()
        '''
        bit = bitreader.readbit()

        if bit == 1:
            return read_treeBranch()
        else:
            bit = bitreader.readbit()
            if bit == 1:
                return read_treeLeaf()
            else:
                return read_end()

    # creates branch, calculates items in each branch
    def read_treeBranch():
        return huffman.TreeBranch (read_prefix(), read_prefix())
        
    # creates leaf, contains 8 bit integer
    def read_treeLeaf():
        return huffman.TreeLeaf (bitreader.readbits(8))
        
    # creates leaf that indicates EOF
    def read_end():
        return huffman.TreeLeaf (None)

    # start recursion
    return read_prefix()



def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.
    
    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """

    def read_node (node):
        if isinstance(node, huffman.TreeBranch):
            # read which way to recurse
            if bitreader.readbit() == 0:
                return read_node(node.left)
            else:
                return read_node(node.right)
        # if node is a leaf, return its value
        else:
            return node.value

    # initiate recursion
    return read_node(tree)


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.

    '''

    bitreader = bitio.BitReader(compressed)
    bitwriter = bitio.BitWriter(uncompressed)

    # read Huffman tree from beginning of file
    tree = read_tree(bitreader)

    # while compressed stream has data
    while True:
        b = decode_byte(tree, bitreader)
        # if we reach the end
        if b == None:
            break
        else:
            # write decoded bytes
            bitwriter.writebits(b,8)


def write_tree(tree, bitwriter):
    '''Write the specified Huffman tree to the given bit writer.  The
    tree is written in the format described above for the read_tree
    function.

    DO NOT flush the bit writer after writing the tree.

    Args:
      tree: A Huffman tree.
      bitwriter: An instance of bitio.BitWriter to write the tree to.
    '''

    # write branch prefix, and left and right of branch
    def write_branch (node):
        bitwriter.writebit(1)
        write_either (node.left)
        write_either (node.right)

    # write leaf prefix and value
    def write_leaf (node):
        bitwriter.writebit(0)
        if node.value != None:
            bitwriter.writebit(1)
            # write value
            bitwriter.writebits(node.value,8)
        # if it is EOF indicator
        else:
            bitwriter.writebit(0)

    # check whether to write branch or leaf
    def write_either (node):
        # if nothing on this path
        if node == None:
            return
        # if branch
        if isinstance(node, huffman.TreeBranch):
            write_branch(node)
        # if leaf
        else:
            write_leaf(node)

    # start recursion
    write_either(tree)


def compress(tree, uncompressed, compressed):
    '''
    First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''

    bitreader = bitio.BitReader(uncompressed)
    bitwriter = bitio.BitWriter(compressed)

    # write tree to the beginning of the file
    write_tree(tree, bitwriter)

    # create encoding table for compressed bits of file using our tree
    table = huffman.make_encoding_table(tree)

    counter = 0

    # read from uncompressed stream until done
    while True:
        try:
            # find path description (tuple) from encoding table
            path = table[bitreader.readbits(8)]
        # if we have reached the end of the file
        except EOFError:
            bitwriter.writebits(0,2)
            # to have a full byte at the end
            counter += 2
            break

        # write the path to the compressed file
        for p in path:
            if p:
                bitwriter.writebit(1)
                counter += 1
            else:
                bitwriter.writebit(0)
                counter += 1

    # find how many bits left to make an even byte
    counter %= 8

    # complete byte with 0s
    while counter:
        bitwriter.writebit(0)
        counter -= 1