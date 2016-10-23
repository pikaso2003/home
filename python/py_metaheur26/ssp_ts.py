"""
ssp_ts.py: Construction and tabu search for the stable set problem.

The Stable Set Problem (SSP) is a combinatorial optimization problem
where: given a graph, find the maximum subset of nodes S such that
there are no edges between nodes in S.  This problem is equivalent to
finding the maximum clique in the complementary graph.

This file contains a set of functions to illustrate construction and a
simple variant of tabu search.

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""
LOG = False      # whether or not to print intermediate solutions
import random
Infinity = 1.e10000

from graphtools import *

def evaluate(nodes, adj, sol):
    """Evaluate a solution.

    Determines:
      - the cardinality of a solution, i.e., the number of nodes in the stable set;
      - the number of conflicts in the solution (pairs of nodes for which there is an edge);
      - b[i] - number of nodes adjacent to i in the stable set;
    """
    card = len(sol)
    b = [0 for i in nodes]
    infeas = 0
    for i in sol:
        for j in adj[i]:
            b[j] += 1
            if j in sol:
                infeas += 1
    return card, infeas/2, b


def construct(nodes, adj):
    """A simple construction method.

    The solution is represented by a set, which includes the vertices 
    in the stable set.

    This function constructs a maximal stable set.
    """
    sol = set([])
    b = [0 for i in nodes]
    indices = list(nodes)
    random.shuffle(indices)
    for ii in nodes:
        i = indices[ii]
        if b[i] == 0:
            sol.add(i)
            for j in adj[i]:
                b[j] += 1
    return sol


def find_add(nodes, adj, sol, b, tabu, tabulen, iteration):
    """Find the best non-tabu vertex for adding into 'sol' (the stable set) """
    xdelta = Infinity
    istar = []
    for i in set(nodes) - sol:
        # if tabu[i] <= iteration:
        if random.random() > float(tabu[i] - iteration)/tabulen:
            delta = b[i]
            if delta < xdelta:
                xdelta = delta
                istar = [i]
            elif delta == xdelta:
                istar.append(i)
            
    if istar != []:
        return random.choice(istar)
    
    print "blocked, no non-tabu move"
    for i in nodes:     # reset tabu information
        tabu[i] = min(tabu[i],iteration)
    return find_add(nodes, adj, sol, b, tabu, tabulen, iteration)


def find_drop(nodes, adj, sol, b, tabu, tabulen, iteration):
    """Find the best non-tabu vertex for removing from 'sol' (the stable set) """
    xdelta = -Infinity
    istar = []
    for i in sol:
        # if tabu[i] <= iteration:
        if random.random() > float(tabu[i] - iteration)/tabulen:
            delta = b[i]
            if delta > xdelta:
                xdelta = delta
                istar = [i]
            elif delta == xdelta:
                istar.append(i)
            
    if istar != []:
        return random.choice(istar)
    
    print "blocked, no non-tabu move"
    for i in nodes:     # reset tabu information
        tabu[i] = min(tabu[i],iteration)
    return find_drop(nodes, adj, sol, b, tabu, tabulen, iteration)


def move_in(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, iteration):
    """Determine and execute the best non-tabu insertion into the solution."""

    # find the best move
    i = find_add(nodes, adj, sol, b, tabu, tabuOUT, iteration)
    # print "{} <- %d\t" % i,
    tabu[i] = iteration + tabuIN
    sol.add(i)

    # update cost structure for nodes connected to i
    deltainfeas = 0
    for j in adj[i]:
        b[j] += 1
        if j in sol:
            deltainfeas += 1
    return deltainfeas


def move_out(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, iteration):
    """Determine and execute the best non-tabu removal from the solution."""

    # find the best move
    i = find_drop(nodes, adj, sol, b, tabu, tabuIN, iteration)
    # print "{} -> %d\t" % i,
    tabu[i] = iteration + tabuOUT
    sol.remove(i)

    # update cost structure for nodes connected to i
    deltainfeas = 0
    for j in adj[i]:
        b[j] -= 1
        if j in sol:
            deltainfeas -= 1
    return deltainfeas


def tabu_search(nodes, adj, sol, max_iter, tabulen, report=None):
    """Execute a tabu search run."""
    n = len(nodes)
    tabu = [0 for i in nodes]

    card, infeas, b = evaluate(nodes, adj, sol)
    assert infeas == 0
    bestsol, bestcard = set(sol), card
    if LOG:
        print "iter:", 0, "\tcard: %d (%d conflicts)" % (card,infeas),\
              "/ best:", bestcard # , "\t", sol
    for it in range(max_iter):
        tabuIN = 1+int(tabulen/100. * card)     # update tabu parameter for inserting vertices
        tabuOUT = 1+int(tabulen/100. * (n-card))# update tabu parameter for removing vertices
        if infeas == 0: # solution is feasible, add a new vertex
            infeas += move_in(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card += 1
        else:           # solution is infeasible, remove a vertex
            infeas += move_out(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card -= 1

        if infeas == 0 and card > bestcard:
            bestsol, bestcard = set(sol), card
            if report:
                report(card, "iter:%d" % it)

        if LOG:
            print "iter:", it+1, "\tcard: %d (%d conflicts)" % (card,infeas),\
                  "/ best:", bestcard # , "\t", sol
            
    # check solution correctness:
    # xcard, xinfeas, xb = evaluate(nodes, adj, bestsol)
    # assert bestcard == xcard and xinfeas == 0
    return bestsol, bestcard
        

if __name__ == "__main__":
    """Tabu search for the Stable Set Problem: sample usage"""
    import sys
    if len(sys.argv) == 1:
        # rndseed = 1	# uncomment for having always the same behavior
        # random.seed(rndseed)
        instance = "randomly created"
        nodes,edges = rnd_graph(100,.5)
        edges = complement(nodes,edges)
        adj = adjacent(nodes, edges)
        max_iterations = 1000
        tabulength = len(nodes)/10
    elif len(sys.argv) == 5:
        instance = sys.argv[1]
        rndseed = int(sys.argv[2])
        random.seed(rndseed)
        tabulength = float(sys.argv[3])
        max_iterations = int(sys.argv[4])
        print "reading file:", instance
        nodes,adj = read_compl_graph(instance)
    else:
        print "usage:", sys.argv[0], "instance seed tabulength iterations"
        exit(-1)

    # function for printing best found solution when it is found
    from time import clock
    init = clock()
    def report_sol(obj,s=""):
        print "cpu:%g\tobj:%g\t%s" % \
              (clock(), obj, s)

    print "*** stable set problem ***"
    print

    print "instance", instance
    sol = construct(nodes,adj)
    print "initial solution:", sol
    xcard, xinfeas, xb = evaluate(nodes, adj, sol)
    print "cardinality: %d (%d conflicts)" % (xcard, xinfeas)
    assert xinfeas == 0
    print

    print "starting tabu search"
    sol, card = tabu_search(nodes, adj, sol, max_iterations, tabulength, report_sol)
    print
    print "final solution: z =", card
    print sol
    print
