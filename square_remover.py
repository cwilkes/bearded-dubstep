import itertools as it
import sys
import random
import os
import math




MAX_MOVES = int(os.environ.get('sr_moves', '10000'))





class SquareRemover(object):
    def __init__(self, rand_seed=None):
        if rand_seed is not None:
            random.seed(rand_seed)
        else:
            random.seed(1)

    def playIt(self, number_colors, board_str, start_seed):
        msr = MySquareRemover(number_colors, board_str, start_seed)
        while msr.move_count() != MAX_MOVES:
            for r, c in r_and_c(1, 1, len(board_str)-2):
                msr.do_move(r, c, random.randint(0, 3))
                if msr.move_count() == MAX_MOVES:
                    break
        lgi('Total filled in: %d', msr.fill_count())
        lgi('MBoar: %s', msr.board)
        return msr.moves_as_array()


class MySquareRemover(object):
    def __init__(self, number_colors, board_str, start_seed):
        if number_colors == 4:
            BUFFER_SIZE = 1
        self.number_colors = number_colors
        self.board = Board(self.number_colors, board_str, start_seed)
        self.moves = list()
        lgi('IBoar: %s' % (self.board, ))

    def move_count(self):
        return len(self.moves)

    def fill_count(self):
        return self.board.fill_count

    def do_move(self, row, col, direction):
        self.board.swap(row, col, direction)
        self.moves.append((row, col, direction))

    def moves_as_array(self):
        ret = list()
        for move in self.moves:
            ret.extend(move)
        return ret


FREE_ZONES = dict()
FREE_ZONES[0] = dict()
FREE_ZONES[0][+0][-1] = (1, 2)
FREE_ZONES[0][-1][+0] = (1, 2)
FREE_ZONES[1][+0][+1] = (0, 3)
FREE_ZONES[1][-1][+0] = (0, 3)
FREE_ZONES[2][+0][-1] = (0, 3)
FREE_ZONES[2][+1][+0] = (0, 3)
FREE_ZONES[3][+0][+1] = (1, 2)
FREE_ZONES[3][+1][+0] = (1, 2)







class Solver(object):
    def __init__(self):
        self.cached = dict()
        self.bit_value_size = dict()

    def _adjust(self, row, col, moves):
        pass

    def _move_in(self, row, col, bit_values):
        size = bit_values.window_size
        solutions = list()
        for (r1, c1), (r2, c2) in r_and_c_outside(size):
            if bit_values.color(r1, c1) == '1':
                tmp = bit_values.copy()
                if tmp.swap(r1, c1, r2, c2):
                    moves = list(self.solve(row, col, tmp))
                    moves.insert(0, (r1, c1, find_direction(r1, c1, r2, c2)))
                    solutions.append(moves)
        best = None
        best_count = sys.maxint
        for moves in solutions:
            if len(moves) < best_count:
                best_count = len(moves)
                best = moves
        return best

    def _solve4(self, bv):
        return None

    def solve(self, row, col, bit_values):
        as_str = str(bit_values)
        if as_str in self.cached:
            return self._adjust(row, col, self.cached[as_str])
        count = bit_values.count()
        if bit_values.window_size == 4:
            if count >= 4:
                moves = self._solve4(bit_values)
                self.cached[as_str] = moves
                return self._adjust(row, col, self.cached[as_str])
            else:
                # have them send be size larger
                return None
        if count < 4:
            # we are bigger than 4 and have less than 4 values to move in
            return None
        # larger than 4 and have more than 4 pieces, so move them in till we get
        # best solution

        if bit_values.window_size == 4 and count < 4:
            return None
        # we have 4 or more in boundaries
        bv2 = bit_values.copy()
        moves = list()
        if bit_values.window_size == 4:
            moves.extend()
            self.cached[as_str] = moves
            return self._adjust(row, col, self.cached[as_str])
        if count == 3:
            moves = self._move_in(row, col, bit_values)
            self.cached[as_str] = moves
            return self._adjust(row, col, self.cached[as_str])
        else:
            return None


class Square(object):
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.nodes = None

    def set_nodes(self, *nodes):
        self.nodes = nodes

    def _find_colors(self, node_number, color):
        distances = list()
        for ring in self.nodes[node_number].rings[node_number]:
            for distance, other_nodes in enumerate(ring.distances):
                for node in other_nodes:
                    if node.color == color:
                        while len(distances) >= distance:
                            distances.append(list())
                        distances[distance].append(node)
        return distances

    def __str__(self):
        return '<S:%s>' % (self.nodes, )

    def find_moves(self, color):
        # first see if can pull in any nearby
        moves = dict()
        free = [list() for _ in range(4)]
        for node_number in range(4):
            distances = self._find_colors(node_number, color)
            my_node = self.nodes[node_number]
            if my_node.color == color:
                # can give these up to others
                if len(distances) > 1:
                    for other_node in distances[1]:
                        delta_row = other_node.row - my_node.row
                        delta_col = other_node.col - my_node.col
                        for pos in FREE_ZONES[node_number][delta_row][delta_row]:
                            free[pos].append(other_node)
            else:
                # just pick the closest one
                for nodes in distances:
                    if len(nodes) > 0:
                        moves[my_node] = nodes[0]
        for node_number in range(4):
            my_node = self.nodes[node_number]
            if my_node.color != color and my_node not in moves:
                # get the first pick from the free nodes
                if len(free[node_number]) > 0:
                    moves[my_node] = free[node_number].pop(0)
        lgi('First tier moves for %s : %s', self, moves)


class Ring(object):
    def __init__(self):
        self.distances = list()

    def add_node(self, node, distance):
        while distance >= len(self.distances):
            self.distances.append(list())
        self.distances[distance].append(node)


class Node(object):
    def __init__(self, row, col, board_size, color):
        self.row, self.col, self.pos, self.color = row, col, color
        self.position = self.row * board_size + self.col
        self.rings = list()
        # 0 = top left, 1 = top right, 2 = bottom left, 3 = bottom right
        self.rings = [Ring() for _ in range(4)]
        self.distances = list()

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return self.position

    def __str__(self):
        return '(%02d,%02d,%d)' % (self.row, self.col, self.color)

    def add_neighbor(self, node):
        delta_row = self.row - node.row
        delta_col = self.col - node.col
        dist = abs(delta_row) + abs(delta_col)
        while dist >= len(self.distances):
            self.distances.append(list())
        # have a dist=0 distances as then can count colors
        self.distances[dist].append(node)
        if delta_row < 0:
            if delta_col < 0:
                self.rings[0].add_node(node, dist)
            elif delta_col > 0:
                self.rings[1].add_node(node, dist)
            else:
                # in both
                self.rings[0].add_node(node, dist)
                self.rings[1].add_node(node, dist)
        elif delta_row > 0:
            if delta_col < 0:
                self.rings[2].add_node(node, dist)
            elif delta_col > 0:
                self.rings[3].add_node(node, dist)
            else:
                self.rings[2].add_node(node, dist)
                self.rings[3].add_node(node, dist)
        else:
            # on the same row
            if delta_col < 0:
                self.rings[2].add_node(node, dist)
            elif delta_col > 0:
                self.rings[3].add_node(node, dist)
            else:
                # this is the same position as the node
                pass


def create_nodes(colors, window_size=3):
    nodes = list()
    board_size = len(colors)
    for row in range(board_size):
        nodes.append([Node(row, col, board_size, colors[row][col]) for col in range(board_size)])
    for r1, c1 in r_and_c(0, 0, board_size):
        for r2, c2 in r_and_c(r1-window_size, c1-window_size, window_size*2):
            if 0 <= r2 < board_size and 0 <= c2 < board_size:
                nodes[r1][c1].add_neighbor(nodes[r2][c2])
    squares = list()
    for r in range(board_size-1):
        squares = [Square(r, c) for c in range(board_size-1)]
    for r1, c1 in r_and_c(0, 0, board_size-1):
        squares[r1][c1].set_nodes(nodes[r1][c1], nodes[r1][c1+1], nodes[r1+1][c1], nodes[r1+1][c1+1])
    return nodes, squares


def create_bit_values(nodes, row, col, color):
    bv = BitValues()
    for r in range(max(0, row-1), min(row+2, len(nodes)-2)):
        for c in range(max(0, col-1), min(col+2, len(nodes)-2)):
            if nodes[r][c].color == color:
                bv.set_val(r, c, '1')
            else:
                bv.set_val(r, c, '0')
    return bv




class Board(object):
    def __init__(self, number_colors, board_str, seed):
        self.number_colors = number_colors
        self.seed = seed
        self.size = len(board_str)
        self.bvs = list()
        self.colors = list()
        self.fill_count = 0
        for r, c in r_and_c(0, 0, self.size):
            my_color = int(board_str[r][c])
            self.colors.append(my_color)
        for color in range(number_colors):
            bv = BitValues(self.size*self.size)
            pos = 0
            for r, c in r_and_c(0, 0, self.size):
                my_color = int(board_str[r][c])
                if my_color == color:
                    bv.set_val(pos, True)
            self.bvs.append(bv)
        self._check_for_squares(None, None, None, None)
        lgi('done init board, score: %d', self.fill_count)

    def _rc(self, pos):
        return pos / self.size, pos % self.size

    def _pos(self, row, col):
        return row*self.size + col

    def color(self, row, col):
        return self.colors[self._pos(row, col)]

    def _is_square(self, r, c):
        c1 = self.color(r, c)
        return c1 == self.color(r, c+1) and c1 == self.color(r+1, c) and c1 == self.color(r+1, c+1)

    def _next_color(self):
        self.seed = (self.seed * 48271) % 2147483647
        return self.seed % self.number_colors

    def _set_color(self, row, col, color):
        current_color = self.color(row, col)
        pos = self._pos(row, col)
        self.colors[pos] = color
        self.bvs[current_color].set_val(pos, False)
        self.bvs[color].set_val(pos, True)
        return current_color

    def _check_for_squares(self, r1, c1, r2, c2):
        # for now do what the demo code does and loop over entire board
        pre = self.fill_count
        while True:
            find = False
            for r, c in r_and_c(0, 0, self.size-1):
                if self._is_square(r, c):
                    self._set_color(r+0, c+0, self._next_color())
                    self._set_color(r+0, c+1, self._next_color())
                    self._set_color(r+1, c+0, self._next_color())
                    self._set_color(r+1, c+1, self._next_color())
                    self.fill_count += 1
                    find = True
                    break
            if not find:
                break
        increase = self.fill_count - pre
        if increase > 0:
            lgi('Filled in %d squares' % (increase, ))
        return increase

    def swap(self, row, col, direction):
        pos1 = self._pos(row, col)
        pos2 = self._pos(row + _adjust_row[direction], col + _adjust_col[direction])
        color1, color2 = self.colors[pos1], self.colors[pos2]
        r2, c2 = self._rc(pos2)
        if color1 == color2:
            #lgi('same color at (%d,%d) move %d to (%d,%d): %d', row, col, direction, r2, c2, color1)
            return
        self._set_color(row, col, color2)
        self._set_color(r2, c2, color1)
        self._check_for_squares(row, col, r2, c2)

    def __str__(self):
        ret = ''
        for pos, _ in enumerate(self.colors):
            if pos != 0 and pos % self.size == 0:
                ret += '/'
            ret += str(_)
        return ret


def main(args):
    lgi('Initialization.  Number moves: %d', MAX_MOVES)
    number_colors = int(sys.stdin.readline().strip())
    size = int(sys.stdin.readline().strip())
    board_str = list()
    for _ in range(size):
        board_str.append(sys.stdin.readline().strip())
    start_seed = int(sys.stdin.readline().strip())
    sr = SquareRemover()
    moves = sr.playIt(number_colors, board_str, start_seed)
    for num in moves:
        print num
    sys.stdout.flush()


if __name__ == '__main__':
    main(sys.argv)