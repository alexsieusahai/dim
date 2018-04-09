from pairing_heap import PairingHeap
from collections import Counter

class TreeLeaf:
    """
    Leaf node of a Huffman tree. Stores the value.

    Should store an 8-bit integer to represent a single byte, or None
    to indicate the special "end of message" character.
    """
    def __init__ (self, value):
        self.value = value


class TreeBranch:
    """
    Simple representation of an internal node on a Huffman tree.
    Just stores the two children.
    """
    def __init__ (self, left, right):
        self.left = left
        self.right = right


def make_tree(freq_table):
    """
    Constructs and returns the Huffman tree from the given frequency table.
    """

    trees = PairingHeap()
    trees.insert(TreeLeaf(None), 1)
    for (symbol, freq) in freq_table.items():
        trees.insert(TreeLeaf(symbol), freq)

    while len(trees) > 1:
        right, rfreq = trees.popmin()
        left, lfreq = trees.popmin()
        trees.insert(TreeBranch(left, right), lfreq+rfreq)

    tree, _ = trees.popmin()
    return tree


def make_encoding_table(huffman_tree):
    """
    Given a Huffman tree, will make the encoding table mapping each
    byte (leaf node) to its corresponding bit sequence in the tree.
    """
    table = {}

    def recurse(tree, path):
        """
        Traces out all paths in the Huffman tree and adds each
        corresponding leaf value and its associated path to the table.
        """
        if isinstance(tree, TreeLeaf):
            # note, if this is the special end message entry then
            # it stores table[None] = path
            table[tree.value] = path
        elif isinstance(tree, TreeBranch):
            # the trailing , has this properly interpreted as a tuple
            # and not just a single boolean value
            recurse(tree.left, path+(False,))
            recurse(tree.right, path+(True,))
        else:
            raise TypeError('{} is not a tree type'.format(type(tree)))

    recurse(huffman_tree, ())
    return table


def make_freq_table(stream):
    """
    Given an input stream, will construct a frequency table
    (i.e. mapping of each byte to the number of times it occurs in the stream).

    The frequency table is actually a counter.
    """

    freqs = Counter()
    buffer = bytearray(512)
    while True:
        count = stream.readinto(buffer)
        freqs.update(buffer[:count])
        if count < len(buffer): # end of stream
            break
    return freqs
