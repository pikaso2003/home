"""
tsp_simple.py: Construction and local optimization for the TSP.

The Traveling Salesman Problem (TSP) is a combinatorial optimization
problem, where given a map (a set of cities and their positions), one
wants to find an order for visiting all the cities in such a way that
the travel distance is minimal.

This file contains a set of functions which are less efficient than
those in file 'tsp.py', but which are easier to understant by beginners.

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""


import math
import random



def exchange_cost(tour, i, j, D):
    """Calculate the cost of exchanging two arcs in a tour.

    Determine the variation in the tour length if
    arcs (i,i+1) and (j,j+1) are removed,
    and replaced by (i,j) and (i+1,j+1)
    (note the exception for the last arc).

    Parameters:
    -t -- a tour
    -i -- position of the first arc
    -j>i -- position of the second arc
    """
    if j < len(tour)-1:
        return (D[tour[i],tour[j]] + D[tour[i+1],tour[j+1]]) - \
               (D[tour[i],tour[i+1]] + D[tour[j],tour[j+1]])
    else:
        return (D[tour[i],tour[j]] + D[tour[i+1],tour[0]]) - \
               (D[tour[i],tour[i+1]] + D[tour[j],tour[0]])


def exchange(tour, i, j):
    """Exchange arcs (i,i+1) and (j,j+1) with (i,j) and (i+1,j+1).

    For the given tour 't', remove the arcs (i,i+1) and (j,j+1) and
    insert (i,j) and (i+1,j+1).
    
    This is done by inverting the sublist of cities between i and j.
    """
    n = len(tour)
    assert i>=0 and i<j-1 and j<n
    path = tour[i+1:j+1]
    path.reverse()
    tour[i+1:j+1] = path


def improve(tour, D):
    """Try to improve tour 't' by exchanging arcs; return improved tour length.
    
    If possible, make a series of local improvements on the solution 'tour',
    using a breadth first strategy, until reaching a local optimum.
    """
    n = len(tour)
    for i in range(0, n-2):
        for j in range(i+2, n):
            if i==0 and j==n-1:
                continue
            dcost = exchange_cost(tour, i , j, D)
            if dcost < 0:     # exchange decreases length
                exchange(tour, i, j);
    return length(tour, D)


def localsearch(tour, z, D):
    """Obtain a local optimum starting from solution t; return solution length.

    Parameters:
    -t -- initial tour
    -z -- length of the initial tour
    -D -- distance matrix
    """
    while 1:
        newz = improve(tour, D)
        if newz < z:
            z = newz
        else:
            break
    return z


def multistart_localsearch(k, n, D, report=None):
    """Do k iterations of local search, starting from random solutions.

    Parameters:
    -k -- number of iterations
    -D -- distance matrix
    -log -- if True, print verbose output

    Returns best solution and its cost.
    """
    bestt=None
    bestz=None
    for i in range(0,k):
        tour = randtour(n)
        z = length(tour, D)
        z = localsearch(tour, z, D)
        if z < bestz or bestz == None:
            bestz = z
            bestt = list(tour)
            if report:
                report(z, tour)
    return bestt, bestz



if __name__ == "__main__":
    """Simple local search for the Travelling Saleman Problem: sample usage."""

    from tsp import mk_matrix, distL2, randtour, length, nearest_neighbor, read_tsplib

    #
    # test the functions:
    #
    
    # random.seed(1)	# uncomment for having always the same behavior
    import sys
    if len(sys.argv) == 1:
        # create a graph with several cities' coordinates
        coord = [(4,0),(5,6),(8,3),(4,4),(4,1),(4,10),(4,7),(6,8),(8,1)]
        n, D = mk_matrix(coord, distL2) # create the distance matrix
        instance = "toy problem"
    else:
        instance = sys.argv[1]
        n, coord, D = read_tsplib(instance)     # create the distance matrix
        # n, coord, D = read_tsplib('INSTANCES/TSP/eil51.tsp')  # create the distance matrix

    # function for printing best found solution when it is found
    from time import clock
    init = clock()
    def report_sol(obj, s=""):
        print "cpu:%g\tobj:%g\ttour:%s" % \
              (clock(), obj, s)


    print "*** travelling salesman problem ***"
    print

    # random construction
    print "random construction + local search:"
    tour = randtour(n)     # create a random tour
    z = length(tour, D)     # calculate its length
    print "random:", tour, z, '  -->  ',   
    z = localsearch(tour, z, D)      # local search starting from the random tour
    print tour, z
    print

    # greedy construction
    print "greedy construction with nearest neighbor + local search:"
    for i in range(n):
        tour = nearest_neighbor(n, i, D)     # create a greedy tour, visiting city 'i' first
        z = length(tour, D)
        print "nneigh:", tour, z, '  -->  ',
        z = localsearch(tour, z, D)
        print tour, z
    print

    # multi-start local search
    print "random start local search:"
    niter = 100
    tour,z = multistart_localsearch(niter, n, D, report_sol)
    assert z == length(tour, D)
    print "best found solution (%d iterations): z = %g" % (niter, z)
    print tour
    print
