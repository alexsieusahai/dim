def precomputeLPS(pattern):
    """
    Precomputes an array called lps, where len(lps) == len(pattern) is true.
    for the ith entry of lps, we know that the pattern from 0 to lps[i] is both
    a proper prefix of pattern, and a suffix of pattern.
    """
    length = 0
    lps = []
    for i in pattern:
        lps.append(0)

    i = 0

    while i < len(pattern):
        if i == 0:
            lps[i] = 0
            i += 1
            continue

        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length-1]
            else:
                lps[i] = 0
                i += 1

    return lps

def kmp(string, pattern):
    """
    textbook implementation of kmp
    returns a list of found indicies
    """
    lps = precomputeLPS(pattern)
    # get lps so we don't have to redo a lot of our work
    i = j = 0
    foundIndicies = []
    while i < len(string):
        if string[i] == pattern[j]:
            # same idea as naive string matching
            i += 1
            j += 1

        if j == len(pattern):  # found a match
            foundIndicies.append(i-j)
            j = lps[j-1]  # skip over what we know will match
            # since we know the string from i-j to i is a
            # proper prefix of the string at index i-j and a
            # proper suffix of the string at index j

        # after j matches, encounter a mismatch
        elif i < len(string) and pattern[j] != string[i]:
            # what do we do?
            if j != 0:
                j = lps[j-1]
                # do not bother matching lps[0,...,j-1] characters
                # since we know they match already by
                # the properties of lps array

            else:
                i += 1

    return foundIndicies

if kmp("AAAAABAAABA","AAAA") != [0,1]:
    print('failed test 1')
if kmp("ABABDABACDABABCABAB", "ABABCABAB") != [10]:
    print('failed test 2')
if kmp("for i in range(10): print(10)", "10") != [15,26]:
    print('failed test 3')
