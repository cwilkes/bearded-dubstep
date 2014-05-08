import itertools as it
import sys

_adjust_row = (-1, 0, 1, 0)
_adjust_col = (0, 1, 0, -1)


def r_and_c(row_start, col_start, size):
    return it.product(range(row_start, row_start+size), range(col_start,col_start+size))


def r_and_c_outside(window_size):
    for c in range(1, window_size-1):
        yield((0, c), (1, c))
    for r in range(1, window_size-1):
        yield((r, window_size-1), (r, window_size-2))
    for c in range(window_size-2, 0, -1):
        yield((window_size-1, c), (window_size-2, c))
    for r in range(window_size-2, 0, -1):
        yield((r, 0), (r, 1))


def r_and_c_outside_sideways(window_size):
    for c in range(1, window_size-1):
        if c != window_size-2:
            yield((0, c), (0, c+1))
            yield((window_size-1, c), (window_size-1, c+1))
        if c != 1:
            yield((0, c), (0, c-1))
            yield((window_size-1, c), (window_size-1, c-1))
    for r in range(1, window_size-1):
        if r != window_size-2:
            yield((r, window_size-1), (r+1, window_size-1))
            yield((r, 0), (r+1, 0))
        if r != 1:
            yield((r, window_size-1), (r-1, window_size-1))
            yield((r, 0), (r-1, 0))


def next_position(row, col, direction):
    return row + _adjust_row[direction], col + _adjust_col[direction]


def find_direction(r1, c1, r2, c2):
    if r1 < r2:
        return 2
    if r1 > r2:
        return 0
    if c1 < c2:
        return 1
    if c1 > c2:
        return 3
    return -1


def lgi(msg, *args):
    print >>sys.stderr, msg % tuple(args)
    sys.stderr.flush()


def get_possible_moves_sideways(bit_values):
    inside_moves = dict()
    for (r1, c1), (r2, c2) in r_and_c_outside(bit_values.window_size):
        inside_moves[(r1, c1)] = r2, c2
    for (r1, c1), (r2, c2) in r_and_c_outside_sideways(bit_values.window_size):
        if bit_values[r1][c1] and not bit_values[r2][c2]:
            middle_r, middle_c = inside_moves[(r2, c2)]
            if not bit_values[middle_r][middle_c]:
                yield ((r1, c1, find_direction(r1, c1, r2, c2)))


def get_possible_moves_in(bit_values):
    last_attempts = list()
    size = len(bit_values)
    for (r1, c1), (r2, c2) in r_and_c_outside(size):
        if bit_values[r1][c1] and not bit_values[r2][c2]:
            move = (r1, c1), (r2, c2)
            if r1 == 0 and (c1 == 1 or c1 == size-2):
                last_attempts.append(move)
            elif r1 == 1 and (c1 == 0 or c1 == size-1):
                last_attempts.append(move)
            elif r1 == bit_values.window_size-2 and (c1 == 0 or c1 == size-1):
                last_attempts.append(move)
            else:
                yield move
    for move in last_attempts:
        yield move