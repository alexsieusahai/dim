# Adapted from http://rosettacode.org/wiki/Bitwise_IO#Python by Roshan
# Shariff.  Licensed under the GNU Free Documentation License 1.2


class BitWriter:

    def __init__(self, f):
        '''f must be an output stream opened in binary mode.'''
        self.accumulator = 0
        self.bcount = 0
        self.out = f

    def __del__(self):
        try:
            self.flush()
        except ValueError:  # I/O operation on closed file
            pass

    def writebit(self, bit):
        '''Writes 1 if 'bit' is true, 0 otherwise.'''
        if self.bcount == 8:
            self.flush()
        if bit:
            self.accumulator |= (1 << (7-self.bcount))
        self.bcount += 1

    def writebits(self, bits, n):
        '''Writes 'n' least significant bits of integer 'bits', start
        with the most significant of these bits.'''
        while n > 0:
            self.writebit(bits & (1 << (n-1)))
            n -= 1

    def flush(self):
        '''MUST CALL WHEN DONE. Writes out any partial bytes to file.'''
        self.out.write(bytes((self.accumulator,)))
        self.accumulator = 0
        self.bcount = 0


class BitReader:

    def __init__(self, f):
        '''f must be an input stream opened in binary mode.'''
        self.accumulator = 0
        self.bcount = 0
        self.input = f

    def readbit(self):
        '''Reads one bit and returns as 1 or 0.'''
        if self.bcount == 0:
            a = self.input.read(1)
            if a:
                self.accumulator = a[0]
                self.bcount = 8
            else:
                raise EOFError('End of file while reading bits')
        self.bcount -= 1
        return (self.accumulator >> self.bcount) & 1

    def readbits(self, n):
        '''Reads n bits and returns them packed into an integer.
        The first bit read will be the most significant of these n bits.'''
        v = 0
        while n > 0:
            v = (v << 1) | self.readbit()
            n -= 1
        return v
