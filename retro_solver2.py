import utils
from utils import lgi


class RetroSolver2(object):
    def __init__(self):
        self.cached = dict()

    def solve(self, bit_values):
        if bit_values in self.cached:
            return self.cached[bit_values]
        if bit_values.count() < 4:
            return None
        if bit_values.window_size == 4:
            return self._solve4(bit_values)
        elif bit_values.window_size == 6:
            return self._solve6(bit_values)
        else:
            raise Exception('Only can deal with sizes 4 and 6 not %d' % (bit_values.window_size, ))

    @staticmethod
    def _is_solved(bit_values):
        return bit_values[1][1] and bit_values[1][2] and bit_values[2][1] and bit_values[2][2]

    @staticmethod
    def _check_move(bit_values, moves_append, prereqs, moves):
        for r, c, val in prereqs:
            if bit_values[r][c] != val:
                return False
        tmp = bit_values.copy()
        good_moves = list()
        for pos in range(0, len(moves), 2):
            r1, c1 = moves[pos]
            r2, c2 = moves[pos+1]
            p = tmp.swap(r1, c1, r2, c2)
            if p:
                lgi('good move with %s', p)
                good_moves.append(p)
            else:
                lgi('Bad move with %s : %s', tmp, (r1,c1,r2,c2))
                return False
        moves_append.extend(good_moves)
        bit_values.replace(tmp)
        return True

    def _solve4(self, bit_values):
        moves = list()
        if self._is_solved(bit_values):
            return moves
        tmp = bit_values.copy()
        for (r1, c1), (r2, c2) in utils.get_possible_moves_in(bit_values):
            p = tmp.swap(r1, c1, r2, c2)
            if p:
                moves.append(p)
        if self._is_solved(tmp):
            return moves
        # see if we can do a double move
        self._check_move(tmp, moves, [(0, 1, True), (1, 1, True), (1, 2, False)], [(1, 1), (1, 2), (0, 1), (1, 1)])
        self._check_move(tmp, moves, [(0, 1, True), (1, 1, True), (2, 1, False)], [(1, 1), (2, 1), (0, 1), (1, 1)])
        self._check_move(tmp, moves, [(1, 0, True), (1, 1, True), (1, 2, False)], [(1, 1), (1, 2), (1, 0), (1, 1)])
        self._check_move(tmp, moves, [(1, 0, True), (1, 1, True), (2, 1, False)], [(1, 1), (2, 1), (1, 0), (1, 1)])
        if self._is_solved(tmp):
            return moves

        self._check_move(tmp, moves, [(0, 2, True), (1, 2, True), (1, 2, False)], [(1, 2), (2, 2), (0, 2), (1, 2)])
        self._check_move(tmp, moves, [(0, 2, True), (1, 2, True), (1, 1, False)], [(1, 2), (1, 1), (0, 2), (1, 2)])
        self._check_move(tmp, moves, [(1, 3, True), (1, 2, True), (1, 1, False)], [(1, 2), (1, 1), (1, 3), (1, 2)])
        self._check_move(tmp, moves, [(1, 3, True), (1, 2, True), (2, 2, False)], [(1, 2), (2, 2), (1, 3), (1, 2)])
        if self._is_solved(tmp):
            return moves

        self._check_move(tmp, moves, [(2, 3, True), (2, 2, True), (2, 1, False)], [(2, 2), (2, 1), (2, 3), (2, 2)])
        self._check_move(tmp, moves, [(2, 3, True), (2, 2, True), (2, 3, False)], [(2, 2), (1, 2), (2, 3), (2, 2)])
        self._check_move(tmp, moves, [(3, 2, True), (2, 2, True), (2, 1, False)], [(2, 2), (2, 1), (3, 2), (2, 2)])
        self._check_move(tmp, moves, [(3, 2, True), (2, 2, True), (1, 2, False)], [(2, 2), (1, 2), (3, 2), (2, 2)])
        if self._is_solved(tmp):
            return moves

        self._check_move(tmp, moves, [(3, 1, True), (2, 1, True), (1, 1, False)], [(2, 1), (1, 1), (3, 1), (2, 1)])
        self._check_move(tmp, moves, [(3, 1, True), (2, 1, True), (2, 2, False)], [(2, 1), (2, 2), (3, 1), (2, 1)])
        self._check_move(tmp, moves, [(2, 0, True), (2, 1, True), (1, 1, False)], [(2, 1), (2, 1), (2, 0), (2, 1)])
        self._check_move(tmp, moves, [(2, 0, True), (2, 1, True), (2, 2, False)], [(2, 1), (2, 2), (2, 0), (2, 1)])
        if self._is_solved(tmp):
            return moves

        # threeway move
        self._check_move(tmp, moves, [(0, 1, True), (1, 1, True), (2, 1, True), (2, 2, False)], [(2, 1), (2, 2), (1, 1), (2, 1), (0, 1), (1, 1)])
        self._check_move(tmp, moves, [(0, 2, True), (1, 2, True), (2, 2, True), (2, 1, False)], [(2, 2), (2, 1), (1, 2), (2, 2), (0, 2), (1, 2)])
        self._check_move(tmp, moves, [(1, 3, True), (1, 2, True), (1, 1, True), (2, 2, False)], [(1, 1), (2, 2), (1, 2), (1, 1), (1, 3), (1, 2)])
        self._check_move(tmp, moves, [(2, 3, True), (2, 2, True), (2, 1, True), (1, 2, False)], [(2, 1), (1, 2), (2, 2), (2, 1), (2, 3), (2, 2)])
        self._check_move(tmp, moves, [(3, 2, True), (2, 2, True), (1, 2, True), (1, 1, False)], [(1, 2), (1, 1), (2, 2), (1, 2), (3, 2), (2, 2)])
        self._check_move(tmp, moves, [(3, 1, True), (2, 1, True), (1, 1, True), (1, 2, False)], [(1, 1), (1, 2), (2, 1), (1, 1), (3, 2), (2, 2)])
        if self._is_solved(tmp):
            return moves

        raise Exception('Do not know what to do with %s : %s' % (bit_values, tmp))


    def _solve6(self, bit_values):
        # we have a chance
        if bit_values.inner_count(1) >= 4:
            moves = list()
            for p in self._solve4(bit_values):
                # could be null
                if p:
                    r, c, move = p
                    moves.append((r+2, c+2, move))
            self.cached[bit_values] = moves
            return moves
        # need to move some from outside in
        tmp = bit_values.copy()
        moves = list()
        for (r1, c1), (r2, c2) in utils.get_possible_moves_in(bit_values):
            moves.append(tmp.swap(r1, c1, r2, c2))
            for r, c, move in self._solve6(tmp):
                moves.append((r, c, move))
            self.cached[bit_values] = moves
            return self.cached[bit_values]
        lgi('Trouble with %s : %s', bit_values, tmp)