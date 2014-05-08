from utils import r_and_c, find_direction, next_position


class InnerBitValue(object):
    def __init__(self, parent, size):
        self.parent = parent
        if type(size) == str:
            self.vals = [_ == '1' for _ in size]
        else:
            self.vals = [False for _ in range(size)]
        self._str, self._count = None, 0
        self._my_str()

    def _my_str(self):
        as_str = ''
        count = 0
        for _ in self.vals:
            if _:
                count+=1
                as_str += '1'
            else:
                as_str += '0'
        self._str = as_str
        self._count = count

    def count(self):
        return self._count

    def __getitem__(self, item):
        return self.vals[item]

    def __setitem__(self, key, value):
        self.vals[key] = value
        self._my_str()
        self.parent._calc_str()

    def __str__(self):
        return self._str

    def __repr__(self):
        return self._str


class BitValues(object):
    def __init__(self, val=4):
        if type(val) == str:
            self.bits = list()
            lines = val.split('/')
            self.window_size = len(lines)
            for r, line in enumerate(lines):
                self.bits.append(InnerBitValue(self, line))
        else:
            self.window_size = val
            self.bits = list()
            for r in range(self.window_size):
                self.bits.append(InnerBitValue(self, self.window_size))
        self._str, self._hash, self._count = None, None, 0
        self._calc_str()

    def run(self, moves):
        tmp = self.copy()
        # if anything looks wrong return the last move that failed
        for r1, c1, direction in moves:
            r2, c2 = next_position(r1, c1, direction)
            if not tmp.swap(r1, c1, r2, c2):
                return r1, c1, direction
        return tmp

    def _calc_str(self):
        as_str = ''
        count = 0
        for ibv in self.bits:
            as_str += str(ibv)
            count += ibv.count()
            as_str += '/'
        self._str = as_str[:-1]
        self._hash = hash(self._str)
        self._count = count

    def make_inner(self, in_blocks=1):
        bv = BitValues(self.window_size - 2*in_blocks)
        for r, c in r_and_c(in_blocks, in_blocks, self.window_size-2*in_blocks):
            bv.bits[r-in_blocks][c-in_blocks] = self.bits[r][c]
        return bv

    def inner_count(self, in_blocks=1):
        count = 0
        for r, c in r_and_c(in_blocks, in_blocks, self.window_size-2*in_blocks):
            count += 1 if self.bits[r][c] else 0
        return count

    def swap(self, r1, c1, r2, c2):
        if self.bits[r1][c1] == self.bits[r2][c2]:
            #print 'no swap from (%d,%d) to (%d,%d) as same color %s' % (r1, c1, r2, c2, self.bits[r1][c1])
            return None
        if abs(r1-r2) + abs(c1-c2) != 1:
            #print 'Cannot move more than one square at a time'
            return None
        self.bits[r1][c1], self.bits[r2][c2] = self.bits[r2][c2], self.bits[r1][c1]
        self._calc_str()
        return r1, c1, find_direction(r1, c1, r2, c2)

    def replace(self, other):
        for r, c in r_and_c(0, 0, self.window_size):
            self.bits[r][c] = other[r][c]

    def count(self):
        return self._count

    def copy(self):
        bv = BitValues(self.window_size)
        for r, c in r_and_c(0, 0, self.window_size):
            bv.bits[r][c] = self.bits[r][c]
        return bv

    def __getitem__(self, item):
        return self.bits[item]

    def __len__(self):
        return self.window_size

    def __hash__(self):
        return self._hash

    def __str__(self):
        return self._str

    def __repr__(self):
        return self._str
