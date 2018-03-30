
def dirBinSearch(dirsLinkedList, dirs, substr, oldIndex):
    """
    Find the directory in dirs such that it begins with substr
        If it exists, return the node
        otherwise, don't do anything

    Note that dirs begins with '..', so we don't want to bin search over that, hence our left index starting at 1
    """

    def check(s,substr):
        """
        If s begins with substr, return True
        else, return False
        """
        if len(substr) > len(s):
            return False

        for i in range(len(substr)):
            if substr[i] != s[i]:
                return False
        return True

    def ithNode(i):
        walk = dirsLinkedList.start
        while i:
            walk = walk.nextNode
            i -= 1
        return walk

    l = 1
    r = len(dirs)-1
    i = 0
    while l <= r:
        m = l + (r-l)//2

        s = dirs[m]

        if check(s,substr):
            return ithNode(m)

        if s > substr:
            #print(s,' > ',substr)
            r = m-1
        else:
            #print(s,' < ',substr)
            l = m+1

    return

if __name__ == '__main__':
    print(dirBinSearch(['..','astr','bstr','cstr','dstr'],'a',-1))
    print(dirBinSearch(['..','AndroidProject','DoAndroidsDream','OfElectricSheep','Proof of Riemann Zeta Function','React-Native Project','zzzz'],'z',-1))
    print(dirBinSearch(['..','AndroidProject','DoAndroidsDream','OfElectricSheep','Proof of Riemann Zeta Function','React-Native Project','zzzz'],'OfElectric',-1))
    print(dirBinSearch(['..','AndroidProject','DoAndroidsDream','OfElectricSheep','Proof of Riemann Zeta Function','React-Native Project','zzzz'],'AndroidProject',-1))
    print(dirBinSearch(['..','README.md','Util','__init__.py','algorithms','constants.py','index.html'],'alg',-1))
