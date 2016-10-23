"""
queens_fast.py: Tabu search for the n-queens problem -- fast construction

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

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""

from queens import display, collisions, exchange
import random
import math
LOG = True
Infinity = 1.e10000

def construct(sol):
    n = len(sol)
    ndiag = 2*n-1       # number of diagonals in the board

    # upward diagonals (index 0 corresponds to the diagonal on upper-left square)
    diag_up = [0 for i in range(ndiag)]

    # downward diagonals (index 0 corresponds to the diagonal on upper-right square)
    diag_dn = [0 for i in range(ndiag)]

    cand = range(n)
    trials = 10*int(math.log10(n)) #number of random trials
    for i in range(n):
        for t in range(trials):
            col_id = random.randint(0,len(cand)-1)
            col = cand[col_id]
            colls = diag_up[i+col]+diag_dn[(n-1)-i+col]
            if colls == 0:
                sol[i] = col
                diag_up[i+col] += 1
                diag_dn[(n-1)-i+col] += 1
                del cand[col_id]
                break
        else:
            mincolls = Infinity
            col_id =- 1
            for j in range(len(cand)):
                colls = diag_up[i+cand[j]] + diag_dn[(n-1)-i+cand[j]]
                if colls < mincolls:
                    mincolls = colls
                    col = cand[j]
                    col_id = j
            sol[i] = col
            diag_up[i+col] += 1
            diag_dn[(n-1)-i+col] += 1
            del cand[col_id]
        # print "row",i,"is assigned to col",col
    return diag_up,diag_dn
            

def fast_tabu_search(sol,diag_up,diag_dn):
    LOG =0
    n=len(sol)
    tabu=[-1]*n
    maxiter=100000
    tabulen=min(10,n)
    for n_iter in range(maxiter):
        for i in range(n-1,-1,-1):
            colls=diag_up[i+sol[i]]+diag_dn[(n-1)-i+sol[i]]
            if colls-2>0:
                istar=i
                break
        else: #no collusion, we finish the search
            break 
        
        #print "swap candidate is",istar
        delta=-999999
        jstar=-1
        for j in range(n):
            if tabu[j]>=n_iter or j==istar: 
                continue
            temp=(diag_up[j+sol[j]]+diag_dn[(n-1)-j+sol[j]]+colls)-\
                  (diag_up[istar+sol[j]]+diag_dn[(n-1)-istar+sol[j]]+\
                   diag_up[j+sol[istar]]+diag_dn[(n-1)-j+sol[istar]])
            if temp>delta:
                delta=temp
                jstar=j
                
        print "iter=",n_iter,"swap",istar,jstar,"delta=",delta
        if jstar==-1: #clear tabu list
            tabulen=int(tabulen/2)+1
            tabu=[-1]*n
        else:
            tabu[istar]=tabu[jstar]=n_iter+random.randint(1,tabulen)
            exchange(istar,jstar,sol,diag_up,diag_dn)
            
        if LOG:
            display(sol)
            up,dn = diagonals(sol)
            print "queens on upward diagonals:", up
            print "queens on downward diagonals:", dn
            ncolls = collisions(up) + collisions(dn)
    

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        n = 1000
    elif  len(sys.argv) == 2:
        n = int(sys.argv[1])
    elif  len(sys.argv) == 3:
        n = int(sys.argv[1])
        rnd = int(sys.argv[2])
        random.seed(rnd)
        print "random seed:", rnd
    else:
        print "usage:", sys.argv[0], "[board_size [rnd_seed]]"
        sys.exit(-1)
        
    #
    # test the functions:
    #
    LOG=0
    random.seed(123)
    # create a random solution
    print "board size:", n
    #sol = range(n)     # set solution equal to [0,1,...,n-1]
    #random.shuffle(sol)        # place it in a random order

    sol=range(n)
    up,dn=construct(sol)
    ncolls = collisions(up) + collisions(dn)
    print "collisions of randomized greedy :", ncolls
    if LOG:
        print "initial solution (random greedy):"
        print "array:" , sol
        display(sol)
        print "queens on upward diagonals:", up
        print "queens on downward diagonals:", dn

    print "starting fast tabu search"
    fast_tabu_search(sol,up,dn)
    ncolls = collisions(up) + collisions(dn)
    print "collisions:", ncolls
    
    #if ncolls != 0:
        #print "\n\n\nstarting tabu search"
        #tabulen = 10
        #maxiter = 100000
        #ncolls = tabu_search(tabulen, maxiter, sol)
    
