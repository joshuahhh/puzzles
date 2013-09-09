# triple-cross
# (joshuah@alum.mit.edu)

# A solution to the wood triple-cross puzzle found at
#   http://www.importsoul.net/woodwork/puzzles/triple-cross-puzzle/

import time
import itertools
import numpy as np
arr = np.array
mat = np.matrix

unfolded_pieces = [arr([[1,1,1,1],
                        [1,1,1,1],
                        [1,1,1,1],
                        [1,1,1,1]]),
                   arr([[0,1,1,0],
                        [0,1,0,0],
                        [0,1,0,0],
                        [0,1,1,0]]),
                   arr([[0,1,1,0],
                        [0,0,1,1],
                        [0,0,1,1],
                        [0,1,1,0]]),
                   arr([[0,1,1,0],
                        [0,1,1,0],
                        [0,1,1,0],
                        [0,1,1,0]]),
                   arr([[0,1,1,0],
                        [0,1,0,0],
                        [1,1,0,0],
                        [1,1,1,1]]),
                   arr([[0,1,1,0],
                        [0,0,1,0],
                        [0,0,1,1],
                        [1,1,1,1]])]
def fold_piece(unfolded_piece):
  folded = np.dstack((unfolded_piece[:,(0,3)], unfolded_piece[:,(1,2)]))
  return np.asarray(np.where(folded == 1)).T * 2 - [3,1,1]
pieces = map(fold_piece, unfolded_pieces)

rot_x = mat([[ 1, 0, 0],
             [ 0, 0,-1],
             [ 0, 1, 0]])
rot_y = mat([[ 0, 0, 1],
             [ 0, 1, 0],
             [-1, 0, 0]])
rot_z = mat([[ 0,-1, 0],
             [ 1, 0, 0],
             [ 0, 0, 1]])
rot_x2 = rot_x**2
rot_x3 = rot_x**3
rot_y2 = rot_y**2
rot_mats = [mat(np.identity(3)), rot_x,        rot_x2,        rot_x3,
            rot_y2,              rot_x*rot_y2, rot_x2*rot_y2, rot_x3*rot_y2]
rots = [(lambda x, mat=mat: mat*x) for mat in rot_mats]

disp_x, disp_y, disp_z = (arr([x]).T for x in ([2,0,0], [0,2,0], [0,0,2]))
poss = [lambda x:       x + disp_y, lambda x:       x - disp_y,
        lambda x: rot_y*x + disp_x, lambda x: rot_y*x - disp_x,
        lambda x: rot_z*x + disp_z, lambda x: rot_z*x - disp_z]

def check_rots(pos_choices, rot_choices):
  """Check a partial solution to the triple-cross.

  Arguments:
  pos_choices -- full set of positions for the six pieces
  rot_choices -- partial set of rotations for the six pieces

  Returns:
  * a solution, in the form of a 4x4x4 array, if one is found
  * None, if no solution exists
  """

  loc_arrays = [np.asarray(pos(rot(piece.T)).T)
                for piece, rot, pos
                in zip(pieces, rot_choices, pos_choices)]
  locs = sum((map(tuple, loc_array) for loc_array in loc_arrays), [])

  if len(locs) == len(set(locs)):  # that is, if there are no overlaps
    if len(rot_choices) == 6:
      # Solution is found! 
      blanks = np.zeros((4,4,4))
      for i, loc_array in enumerate(loc_arrays):
        x,y,z = ((loc_array.T+3)/2).astype(int)
        blanks[x, y, z] = i+1
      return blanks
    else:
      for rot in rots:
        res = check_rots(pos_choices, rot_choices + [rot])
        if res != None: return res
  return None

now = time.time()
for i, pos_choices in enumerate(itertools.permutations(poss[1:])):
  res = check_rots([poss[0]] + list(pos_choices), [])
  if res != None:
    print "SOLUTION:"
    print res
    print "(%.2f seconds)" % (time.time() - now)
    break
