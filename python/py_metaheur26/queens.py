"""
queens.py: Tabu search for the n-queens problem

The problem consists of finding the positions of n queens on an n x n
chess board, in such a way that none of them is able to capture any
other.  The moves of a queen on a chess board are through horizontal
and vertical lines, and on diagonals.  Therefore, there can not be
more than one queen on the same row, on the same column, or on the
same diagonal (either ascending or descending).

This file contains a set of functions to illustrate how to use tabu
search for solving this problem.

For having no rook attacks, there cannot be more that one queen on
each row, and no more that one queen on each column.  In other words,
there must be exactly one queen on each row and on each column.
With this in mind, the position of the queens is hold in an array with
size n, with each element being a different integer from 0 to n-1. The
i-th element of the array corresponds to the queen of row i (starting
from row 0).  The integer contained on the i-th element of the array
corresponds to the column on which the queen in row i is.

Solution construction is random (using a permutation), and the
neighborhood for local search consists of solutions with the column
of two queens exchanged.

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""

import random

def display(sol):
    """Nicely print the board with queens at positions given in sol"""
    n = len(sol)
    for i in range(0,n):
        for j in range(0,n):
            if sol[i] == j:
                print 'o',
            else:
                print ".",
        print


def diagonals(sol):
    """Determine number of queens on each diagonal of the board.

    Returns a tuple with the number of queens on each of the upward
    diagonals and downward diagonals, respectively
    """

    n = len(sol)        # size of the board
    ndiag = 2*n-1       # number of diagonals in the board

    # upward diagonals (index 0 corresponds to the diagonal on upper-left square)
    diag_up = [0 for i in range(ndiag)]

    # downward diagonals (index 0 corresponds to the diagonal on upper-right square)
    diag_dn = [0 for i in range(ndiag)]

    # count the number of times each diagonal is being attacked
    for i in range(n):
        # upward diagonal being attacked by
        # the queen in row i (which is in column sol[i])
        d = i + sol[i]  # index of diagonal
        diag_up[d] += 1

        # downward diagonal being attacked by
        # the queen in row i (which is in column sol[i])
        d = (n-1) + sol[i] - i  # index of diagonal
        diag_dn[d] += 1

    return diag_up, diag_dn


def collisions(diag):
    """Returns the total number of collisions on the diagonal."""
    ncolls = 0
    for i in diag:
        if i>1:         # i.e., more that one queen on this diag
            ncolls += i-1
    return ncolls


def exchange(i, j, sol, diag_up, diag_dn):
    """Exchange the queen of row i with that of row j; update diagonal info."""

    n = len(sol)

    # diagonals not attacked anymore
    d = i + sol[i]; diag_up[d] -=  1
    d = j + sol[j]; diag_up[d] -=  1

    d = (n-1) - i + sol[i]; diag_dn[d] -= 1
    d = (n-1) - j + sol[j]; diag_dn[d] -= 1

    # exchange the positions 'i' and 'j'
    sol[i], sol[j] = sol[j], sol[i]

    # diagonals that started being attacked
    d = i + sol[i]; diag_up[d] +=  1
    d = j + sol[j]; diag_up[d] +=  1

    d = (n-1) - i + sol[i]; diag_dn[d] += 1
    d = (n-1) - j + sol[j]; diag_dn[d] += 1


def decrease(di,dj,ni,nj):
    """Compute collisions removed when queens are removed.

    Parameters:
    - di, dj -- diagonals where queens are currently placed
    - ni, nj -- number of queens on these diagonals
    """
    delta = 0
    if ni >= 2: delta -= 1
    if nj >= 2: delta -= 1
    if di == dj and ni == 2: delta += 1 # discounted one in excess, replace it
    return delta


def increase(di,dj,ni,nj):
    """Compute new collisions when queens are positioned.

    Parameters:
    - di, dj -- diagonals where queens will be placed
    - ni, nj -- number of queens on these diagonals
    """
    delta = 0
    if ni >= 1: delta += 1
    if nj >= 1: delta += 1
    if di == dj and ni == 0: delta += 1 # on the same diagonal
    return delta
    

def evaluate_move(i, j, sol, diag_up, diag_dn):
    """Evaluate exchange of queen of row i with that of row j."""

    delta = 0
    n = len(sol)

    # diagonals not attacked anymore if move is accepted
    upi = i + sol[i]            # current upward diagonal of queen in row i
    upj = j + sol[j]            #                                         j
    delta += decrease(upi,upj,diag_up[upi],diag_up[upj])

    dni = (n-1) + sol[i] - i    # current downward diagonal of queen in row i
    dnj = (n-1) + sol[j] - j    #                                           j
    delta += decrease(dni,dnj,diag_dn[dni],diag_dn[dnj])

    # diagonals that started being attacked
    upi = i + sol[j]            # new upward diagonal for queen in row i
    upj = j + sol[i]            #                                      j
    delta += increase(upi,upj,diag_up[upi],diag_up[upj])
    
    dni = (n-1) + sol[j] - i    # new downward diagonal of queen in row i
    dnj = (n-1) + sol[i] - j    #                                       j
    delta += increase(dni,dnj,diag_dn[dni],diag_dn[dnj])

    return delta


    
def find_move(n_iter, tabu, best_colls, sol, diag_up, diag_dn, ncolls):
    """Return a tuple (i,j) with the best move.

    Checks all possible moves from the current solution, and choose the one that:
         * is not TABU, or
         * is TABU but satisfies the aspiration criterion

    The candidate list is composed of all the possibilities
    of swapping two lines.

    ParameterS:
    """

    n = len(sol)
    best_delta = n      # value of best found move
    for i in range(0,n-1):
        for j in range(i+1,n):
            delta = evaluate_move(i,j,sol,diag_up,diag_dn)

            print "move %d-%d" % (i,j), "-> delta=%d;" % delta,
            if tabu[i] >= n_iter:
                print "move is tabu;",
                if ncolls + delta < best_colls:
                    print "aspiration criterion is satisfied;",
            print
                
            if (tabu[i] < n_iter         # move is not tabu,
                or ncolls + delta < best_colls): # or satisfies aspiration criterion
                if delta < best_delta:
                    best_delta = delta
                    best_i = i
                    best_j = j

    return best_i, best_j, best_delta


def local_search(sol):
    """Local search: find local optimum starting from sol.
    Returns number of collisions of the local optimum.
    """

    n = len(sol)
    diag_up,diag_dn = diagonals(sol)
    print "\ninitial board"
    display(sol)
    ncolls = collisions(diag_up) + collisions(diag_dn)
    print "collisions:", ncolls

    n_iter = 0
    while True:
        n_iter += 1
        print "\niteration", n_iter

        improved = False
        for i in range(0,n-1):
            for j in range(i+1,n):
                delta = evaluate_move(i,j,sol,diag_up,diag_dn)
                if delta < 0:
                    print "improving move: change rows ", i, "and", j, ", delta", delta
                    improved = True

                    # execute the improvement: update the board
                    exchange(i, j, sol, diag_up, diag_dn)
                    ncolls += delta

                    # display current solution:
                    display(sol)
                    print "collisions:", ncolls

        if not improved:
            return ncolls


def tabu_search(tabulen, maxiter, sol):
    """Tabu search: find solution starting search from sol.

    Parameters:
    - tabulen: number of tabu iterations after a move is done
    - maxiter    - (absolute) maximum number of iterations
    - sol - starting solution; later updated with the best found solution

    Returns number of collisions of the local optimum.
    """
    n = len(sol)
    diag_up,diag_dn = diagonals(sol)
    print "\ninitial board"
    display(sol)
    ncolls = collisions(diag_up) + collisions(diag_dn)
    print "collisions:", ncolls

    n_iter = 0          # iteration count
    iter_best = 0       # iteration at which best solution was found
    best = list(sol)    # copy of the best solution found
    best_colls = ncolls
    # tabu information (iteration until which move from 'i' is forbidden):
    tabu = [0 for i in range(n)]

    while (n_iter < maxiter)  and  (best_colls != 0):
        n_iter += 1

        print "\niteration", n_iter

        # determine the best move in the current neighborhood:
        (i,j,delta) = find_move(n_iter, tabu, best_colls, sol, diag_up, diag_dn, ncolls)
        print "best move is: change rows ", i, "and", j, ", delta", delta

        # update the board, executing the best move:
        exchange(i, j, sol, diag_up, diag_dn)
        ncolls += delta

        # update the tabu structure:
        # moves involving i will be tabu for 'tabulen' iterations
        tabu[i] = n_iter + tabulen

        # check if we improved the best:
        if ncolls < best_colls:
            iter_best = n_iter
            best = list(sol)
            best_colls = ncolls

        # display current solution:
        display(sol)
        print "collisions:", ncolls

    # copy best solution found 
    sol = best  
    ncolls = best_colls

    print
    print "final solution (found at iteration", iter_best, ")"
    print "final tabu list:"
    print tabu
    display(sol)
    print "collisions:", ncolls
    return ncolls


if __name__ == "__main__":
    """Tabu search for the N-Queens problem: sample usage."""
    
    import sys
    if len(sys.argv) == 1:
        n = 8
    elif  len(sys.argv) == 2:
        n = int(sys.argv[1])
    elif  len(sys.argv) == 3:
        n = int(sys.argv[1])
        rnd = int(sys.argv[2])
        random.seed(rnd)
        print "random seed:", rnd
    else:
        print "usage:", sys.argv[0], "[board_size [rnd_seed]]"
        exit(-1)
        
    print "*** graph partitioning problem ***"
    print

    #
    # test the functions:
    #
    
    # create a random solution
    print "instance randomly created"
    print "board size:", n
    sol = range(n)      # set solution equal to [0,1,...,n-1]
    random.shuffle(sol) # place it in a random order
    print "initial solution (random):"
    print "array:" , sol
    display(sol)
    up,dn = diagonals(sol)
    print "queens on upward diagonals:", up
    print "queens on downward diagonals:", dn
    ncolls = collisions(up) + collisions(dn)
    print "collisions:", ncolls

    print "\n\n\nstarting local search"
    ncolls = local_search(sol)

    if ncolls != 0:
        print "\n\n\nstarting tabu search"
        tabulen = n/2
        maxiter = 100000
        ncolls = tabu_search(tabulen, maxiter, sol)
    
    else:
        print "local optimum has no collisions"
        display(sol)
        print "\nno further improvements are possible, not doing tabu search"
    exit(0)
