import utils
from utils import lgi
from models import BitValues
import sys


class RetroSolver(object):
    def __init__(self):
        self.raw = dict()
        self.solved = dict()

    def solve(self, bit_values):
        if bit_values in self.solved:
            return self.solved[bit_values]
        if bit_values.window_size == 4:
            if bit_values.count() < 4:
                return None
            else:
                moves = self._solve4(bit_values)
                if moves:
                    self.solved[bit_values] = moves
                return moves
        # size 6
        if bit_values.count() < 4:
            return None
        if bit_values.inner_count() >= 4:
            # need to expand this
            sol2 = list()
            for r, c, move in self.solve(bit_values.make_inner()):
                sol2.append((r+2, c+2, move))
            self.solved[bit_values] = sol2
            return self.solved[bit_values]
        # have less that 4 on inner count but 4 or more total
        for (r1, c1), (r2, c2) in utils.get_possible_moves_in(bit_values):
            tmp = bit_values.copy()
            tmp.swap(r1, c1, r2, c2)
            moves = list(self.solve(tmp))
            moves.insert(0, (r1, c1, utils.find_direction(r1, c1, r2, c2)))
            self.solved[bit_values] = moves
            return self.solved[bit_values]

    def _solve4(self, bit_values):
        count = bit_values.inner_count(1)
        if count == 4:
            return None
        # 4x4 box with at least 4 on tiles
        tmp = bit_values.copy()
        possible_moves = utils.get_possible_moves_in(bit_values)
        moves = list()
        try:
            (r1, c1), (r2, c2) = next(possible_moves)
            #lgi('Trying simple move for %s', tmp)
            tmp.swap(r1, c1, r2, c2)
            moves.append((r1, c1, utils.find_direction(r1, c1, r2, c2)))
            x = self._solve4(tmp)
            if x is None:
                # solved
                #lgi('Solved for %s with %s', bit_values, moves)
                self.solved[bit_values] = moves
                return self.solved[bit_values]
            else:
                moves.extend(x)
                #lgi('No solve for %s : %s', bit_values, moves)
                return moves
        except Exception as ex:
            # ran out of easily moves in
            pass
        # perhaps we can slide a tile to the side and then have it moved down
        possible_moves = utils.get_possible_moves_sideways(tmp.window_size)
        try:
            (r1, c1), (r2, c2) = next(possible_moves)
            lgi('Trying side move for %s', tmp)
            tmp.swap(r1, c1, r2, c2)
            moves.append((r1, c1, utils.find_direction(r1, c1, r2, c2)))
            x = self._solve4(tmp)
            if x is None:
                # solved
                self.solved[bit_values] = moves
                return self.solved[bit_values]
            else:
                moves.extend(x)
                return moves
        except:
            # rare to get here
            pass
        # can get here if like this: 0000/0110/0011/0000
        for (r1, c1), (r2, c2) in utils.r_and_c_outside(tmp.window_size):
            if tmp.hit(r1, c1):
                # r2, c2 is in the inside ring but it is full, so look to move some around
                r3, c3 = utils.next_position(r2, c2, utils.find_direction(r1, c1, r2, c2))
                lgi('looking at (%d,%d) -> (%d,%d) -> (%d,%d)', r1, c1, r2, c2, r3, c3)
                # if this is not a hit move into it
                if bit_values.hit(r3, c3):
                    lgi('Need to do inner sideways move')
                    if r1 == 0:
                        if c1 == 1:
                            r4, c4 = 2, 2
                        else:
                            r4, c4 = 2, 1
                    elif r1 == 1:
                        if c1 == 0:
                            r4, c4 = 2, 2
                        else:
                            r4, c4 = 2, 1
                    elif r1 == 2:
                        if c1 == 0:
                            r4, c4 = 1, 1
                        else:
                            r4, c4 = 1, 2
                    elif r1 == 3:
                        if c1 == 1:
                            r4, c4 = 1, 2
                        else:
                            r4, c4 = 1, 1
                    if tmp.hit(r4, c4):
                        lgi('give up, cannot figure out %s', tmp)
                    else:
                        tmp.swap(r3, c3, r4, c4)
                        moves.append((r3, c3, utils.find_direction(r3, c3, r4, c4)))
                        # shouldn't have to do this
                        tmp.swap(r2, c2, r3, c3)
                        moves.append((r2, c2, utils.find_direction(r2, c2, r3, c3)))
                        tmp.swap(r1, c1, r2, c2)
                        moves.append((r1, c1, utils.find_direction(r1, c1, r2, c2)))
                else:
                    tmp.swap(r2, c2, r3, c3)
                    moves.append((r2, c2, utils.find_direction(r2, c2, r3, c3)))
                x = self._solve4(tmp)
                if x is None:
                    # solved
                    self.solved[bit_values] = moves
                    return self.solved[bit_values]
                else:
                    moves.extend(x)
                    # not sure if this is correct
                    return moves

        lgi('Should not get here %s', bit_values)
        return None


def main(args):
    rs = RetroSolver()
    for bv in (BitValues(as_str=_) for _ in args[1:]):
        print 'bv', bv, '=>', rs.solve(bv)
    print 'cached'
    for key, val in rs.solved.items():
        print key, val


if __name__ == '__main__':
    main(sys.argv)