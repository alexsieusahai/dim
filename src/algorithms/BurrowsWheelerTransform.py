# https://gist.github.com/dmckean/9723bc06254809e9068f
# code by github.com/dmckean
from operator import itemgetter

def burrowsWheeler (s):
	"""
	input string s
	output string s'

	transformed string is more easily compressible, contains more repeat strings
	to obtain original string use InverseBurrowsWheeler()
	"""

	length = len(s)
	m = sorted([s[i:length]+s[0:i] for i in range(length)])
	I = m.index(s)
	L = ''.join([q[-1] for q in m])
	return (I, L)

def inverseBurrowsWheeler (I, L):
	"""
	input I: number that helps to reverse the BWT
	input L: transformed string

	output S: original string before BWT
	"""

	n = len(L)
	X = sorted([(i, x) for i, x in enumerate(L)], key=itemgetter(1))

	T = [None for i in range(n)]
	for i, y in enumerate(X):
	    j, _ = y
	    T[j] = i

	Tx = [I]
	for i in range(1, n):
	    Tx.append(T[Tx[i-1]])

	S = [L[i] for i in Tx]
	S.reverse()
	return ''.join(S)



if __name__ == "__main__":
	s = "Hello my name is amir and this is my sentence which hopefully soon will be transformed"
	(I,L) = burrowsWheeler(s)
	s_t = inverseBurrowsWheeler(I,L)
	print (s == s_t)
	print(s)
	print(s_t)