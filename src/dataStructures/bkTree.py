import time

class bk_tree(object):
    """
    Tree data structure that allows for fast querying of matches
    given a dictionary of words to iterate over using Levenshtein distance.

    Each node in the tree is the value (a word) and a dictionary of children
    for each of the nodes.

    When reading the code, remember the definition of a bk tree:
        Each node has one unique distance

    Methods:
    add
    find
    """

    def __init__(self):
        """
        Initialize a bk tree for spellchecking with a wordlist.
        This bk tree uses Levenshtein distance.
        Each node is a list containing the node value and its children.

        The idea is summarized below:
        Each node has one unique distance; if not, walk down the tree and add it
        to the only place that doesn't have that unique distance filled.

        Gets the words from words.txt
        """
        self.root = None
        self.words_in_tree = 0
        self.fileName = 'dataStructures/words.txt'
        for word in open(self.fileName):
            print(word[:-1])
            self.add(word[:-1])
            self.words_in_tree += 1
            if self.words_in_tree > 100:
                break

    def find(self, word, max_distance, node=-1):
        """
        Find a word within the tree that is within [0, maxDistance] distance
        from word, and return a list of tuples (item, distance) ordered by distance
        to iterate through.
        """
        if node == -1:  # garbage value
            node = self.root
        if node is None:
            return []  # empty so no matches possible

        #print('im looking at',node)
        possible_matches = []
        (node_val, children) = node

        distance = levenshtein_distance(word, node_val)
        print('the ld for '+word+' and '+node_val+' is ',distance)
        if distance <= max_distance:
            possible_matches.append(node_val)
            #print('adding',node_val,'to possible_matches')

        low_bound = distance - max_distance
        if low_bound < 0:
            low_bound = 1
        high_bound = distance + max_distance

        while low_bound < high_bound:  # walk through the node for any matches
            next_node = children.get(low_bound)
            #print('low bound is',low_bound)
            #print('next node is '+str(next_node))
            temp = []
            if next_node:
                temp = self.find(word, max_distance, node=next_node)
            for possible_match in temp:
                possible_matches.append(possible_match)
            low_bound += 1

        return possible_matches

    def add(self, word):
        """
        add the node to the tree
        """
        node = self.root
        if node is None:  # haven't built up the tree yet
            self.root = (word, {})
            #print('setting root to ',word)
            return

        while node is not None:
            # walk through the tree
            node_val, children = node
            distance = levenshtein_distance(word, node_val)
            node = children.get(distance)  # walk down that way

        children[distance] = (word, {})
        #print('setting child of',node_val,'with value',distance,'to the word',word)

def levenshtein_distance(word, node_val):
    """
    Finds and returns the levenshtein distance between word and node_val
    """

    memo = {}

    # time for a closure!
    def memo_levenshtein_distance(word, i, node_val, j):
        if (word, i, node_val, j) in memo:
            return memo[(word, i, node_val, j)]

        if len(word) - i == 0:
            return len(node_val) - j
        if len(node_val) - j == 0:
            return len(word) - i
        if word[i] != node_val[j]:
            cost = 1
        else:
            cost = 0

        distance = min(memo_levenshtein_distance(word, i+1, node_val, j) + 1,
                   memo_levenshtein_distance(word, i, node_val, j+1) + 1,
                   memo_levenshtein_distance(word, i+1, node_val, j+1) + cost)

        memo[(word, i, node_val, j)] = distance
        return distance

    return memo_levenshtein_distance(word, 0, node_val, 0)


if __name__ == '__main__':
    startTime = time.clock()
    bktree = bk_tree()
    endTime = time.clock()
    print('setting up bktree took',endTime-startTime,'seconds')

