# minesweeper
# (joshuah@alum.mit.edu)

# A demonstration of how to use the CVXOPT library's integer linear
# programming function to solve a minesweeper-like puzzle.

# The puzzle is "Schedule A" of "Form 1515" of the 2007 Microsoft
# Puzzle Challenge, which can be found at
#   https://www.collegepuzzlechallenge.com/Archive/2007/
# The raw data from that puzzle was copied-and-pasted from the puzzle
# PDF into the file minesweeper.txt, found in this directory.

import cvxopt, cvxopt.glpk

class Grid:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def cells(self):
        return [(x,y) for x in range(self.w) for y in range(self.h)]

    def in_range(self, x, y):
        return (0 <= x < self.w) and (0 <= y < self.h)

    def neighbors(self, x, y, disps):
        return [(x+dx, y+dy) for (dx, dy) in disps
                if self.in_range(x+dx, y+dy)]

    def sparse_to_dense(self, d):
        return [[d[(i, j)] for i in range(self.w)] for j in range(self.h)]
    
    @staticmethod
    def symmetrize(x, y):
        return set([(x,y), (y,x), (x,-y), (-y,x),
                    (-x,y), (y,-x), (-x,-y), (-y,-x)])

def solve_boolean_system(eqs):
    vars = list(set().union(*((term[1] for term in eq['lhs']) for eq in eqs)))
    obj2ind = dict((obj, ind) for (ind, obj) in enumerate(vars))
    x, I, J = zip(*sum([[(term[0], i, obj2ind[term[1]]) for term in eq['lhs']]
                        for i, eq in enumerate(eqs)], []))
    A = cvxopt.spmatrix(x, I, J)
    b = cvxopt.matrix([eq['rhs'] for eq in eqs], tc='d')
    status, x = cvxopt.glpk.ilp(None,
                                cvxopt.matrix([[0.]]*(len(vars))),
                                cvxopt.matrix([0.]),
                                A, b, set(), set(range(len(vars))))
    return dict((obj, x[i]) for i, obj in enumerate(vars))


data = map(int, list(open("minesweeper.txt")))
ar1 = [data[i::30] for i in range(15)]
ar2 = [data[i::30] for i in range(15,30)]

grid = Grid(15, 15)
knights_moves = Grid.symmetrize(1, 2)

for rhs in [ar1, ar2]:
    equations = [{'lhs': [(1, n) for n in grid.neighbors(x, y, knights_moves)],
                  'rhs': rhs[x][y]}
                 for (x, y) in grid.cells()]
    sol = grid.sparse_to_dense(solve_boolean_system(equations))
    def format(x):
        return u"\u2588" if float(x)>0.5 else ' '
    print "\n".join(["".join(map(format,sol[i])) for i in range(15)])
