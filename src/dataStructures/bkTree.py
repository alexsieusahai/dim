

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

    def __init__(self, words=[]):
        """
        Initialize a bk tree for spellchecking with a wordlist.
        This bk tree uses Levenshtein distance.
        Each node is a list containing the node value and its children.

        The idea is summarized below:
        Each node has one unique distance; if not, walk down the tree and add it
        to the only place that doesn't have that unique distance filled.
        """
        self.root = None
        for word in words:
            self.add(word)

    def find(self, word, max_distance, node=self.root):
        """
        Find a word within the tree that is within [0, maxDistance] distance
        from word, and return a list of tuples (item, distance) ordered by distance
        to iterate through.
        """
        if node is None:
            return []  # empty so no matches possible

        possible_matches = []
        (node_val, children) = node

        distance = levenshtein_distance(word, node_val)
        if distance <= max_distance:
            possible_matches.append(word)

        low_bound = distance - max_distance
        if low_bound < 0:
            low_bound = 1
        high_bound = distance + max_distance

        while low_bound < high_bound:  # walk through the node for any matches
            next_node = children.get(distance)
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
            return

        while node is not None:
            # walk through the tree
            node_val, children = node
            distance = levenshtein_distance(word, node_val)
            node = children.get(distance) # walk down that way

        children[distance] = (word, {})


if __name__ == "__main__":
    print('main')
