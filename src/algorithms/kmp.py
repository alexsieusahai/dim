def precomputeLPS(pattern):
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
    lps = precomputeLPS(pattern)
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

        elif i < len(string) and pattern[j] != string[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1

    return foundIndicies

if kmp("AAAAABAAABA","AAAA") != [0,1]:
    print('failed test 1')
if kmp("ABABDABACDABABCABAB", "ABABCABAB") != [10]:
    print('failed test 2')
if kmp("for i in range(10): print(10)", "10") != [15,26]:
    print('failed test 3')
