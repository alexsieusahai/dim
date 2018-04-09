import multiprocessing as mp
from dataStructures.bkTree import bk_tree

def testfcn(bktree, word, max_dist):
    print(word)
    print(bktree.find(word, max_dist))


if __name__ == "__main__":
    bktree = bk_tree()
    processes = [mp.Process(target=testfcn, args=(bktree, x, 1)) for x in ['the', 'on', 'with', 'other', 'get', 'car']]
    for process in processes:
        process.start()

    for process in processes:
        process.join()
    print('done')

"""
This is a VERY rudimentary idea of how to use multiprocessing
"""
