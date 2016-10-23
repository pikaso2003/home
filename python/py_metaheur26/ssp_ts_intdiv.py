"""
ssp_ts.py: Construction and tabu search for the stable set problem.

The Stable Set Problem (SSP) is a combinatorial optimization problem
where: given a graph, find the maximum subset of nodes S such that
there are no edges between nodes in S.  This problem is equivalent to
finding the maximum clique in the complementary graph.

This file contains a set of functions to illustrate tabu search with
diversification/intensification

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""

LOG = False     # whether or not to print intermediate solutions
import random
Infinity = 1.e10000

from graphtools import *
from ssp_ts import evaluate, construct, move_in, move_out


def diversify(nodes, adj, v):
    """Find a maximal stable set, starting from node 'v'"""
    b = [0 for i in nodes]
    sol = set([v])
    for j in adj[v]:
        b[j] += 1

    indices = list(nodes)
    random.shuffle(indices)
    for ii in nodes:
        i = indices[ii]
        if i == v:
            continue
        if b[i] == 0:
            sol.add(i)
            for j in adj[i]:
                b[j] += 1
    return sol


def ts_intens_divers(nodes, adj, sol, max_iter, tabulen, report):
    """Execute a tabu search run using intensification/diversification."""
    n = len(nodes)
    tabu = [0 for i in nodes]

    card, infeas, b = evaluate(nodes, adj, sol)
    assert infeas == 0
    bestsol, bestcard, bestb = set(sol), card, list(b)

    D = 1       # self-tuning diversification parameter
    count = 0   # counter for consecutive non-improving iterations
    lastcard = card
    if LOG:
        print "iter:", 0, "non-impr: %d/%d" % (count,D), \
              "\tcard: %d (%d conflicts)" % (card,infeas), "/ best:", bestcard # , "\t", sol
    for it in range(max_iter):
        tabuIN = 1+int(tabulen/100. * card)     # update tabu parameter for inserting vertices
        tabuOUT = 1+int(tabulen/100. * (n-card))# update tabu parameter for removing vertices
        if infeas == 0:         # solution is feasible, add a new vertex
            infeas += move_in(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card += 1
        else:           # solution is infeasible, remove a vertex
            infeas += move_out(nodes, adj, sol, b, tabu, tabuIN, tabuOUT, it)
            card -= 1

        if LOG:
            print "iter:", it+1, "non-impr: %d/%d" % (count,D), \
                  "\tcard: %d (%d conflicts)" % (card,infeas), "/ best:", bestcard # , "\t", sol

        if infeas == 0 and card > bestcard:
            # improved best found solution, intensify search
            bestsol, bestcard, bestb = set(sol), card, list(b)
            if report:
                report(card, "iter:%d" % it)
            if LOG:
                print "*** intensifying: clearing tabu list***"
            tabu = [min(tabu[i],it) for i in nodes]     # clear tabu list
            count = 0
        elif infeas == 0 and card > lastcard:
            count = 0   # reset non-improving iterations counter
        else:
            count += 1

        if count > D:   # exceeded allowed non-improving iterations, restart int/div cycle
            if D % 2 == 0:      # intensification: switch to best found solution
                if LOG:
                    print "*** intensifying: switching to best found solution ***"
                sol, card, b = set(bestsol), bestcard, list(bestb)
                infeas = 0
                # keep tabu list unchanged, for ensuring a different path
            else:       # diversification: construct maximal stable set from less used vertex
                if LOG:
                    print "*** diversifying: constructing maximal set from less used vertex ***"
                # use the tabu history as long-term memory:
                cand = []
                mintabu = Infinity
                for j in set(nodes) - sol:      # find less used vertex (smallest tabu)
                    if tabu[i] < mintabu:
                        cand = [i]
                    if tabu[i] == mintabu:
                        cand.append(i)
                v = random.choice(cand)
                
                sol = diversify(nodes,adj,v)
                card, infeas, b = evaluate(nodes, adj, sol)
                if infeas == 0 and card > bestcard:
                    bestsol, bestcard, bestb = set(sol), card, list(b)
                    if report:
                        report(card, "iter:%d" % it)
                tabu = [min(tabu[i],it) for i in nodes] # clear tabu list

            count = 0   # reset counter
            D += 1      # increase self-tuning parameter

        if infeas == 0:
            lastcard = card
            
    # check solution correctness:
    # xcard, xinfeas, xb = evaluate(nodes, adj, bestsol)
    # assert bestcard == xcard and xinfeas == 0
    return bestsol, bestcard
        

if __name__ == "__main__":
    """Tabu search for the Stable Set Problem:
         sample usage with intensification/diversification
    """
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
    sol, card = ts_intens_divers(nodes, adj, sol, max_iterations, tabulength, report_sol)
    print
    print "final solution: z =", card
    print sol
    print
