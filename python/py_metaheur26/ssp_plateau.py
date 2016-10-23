"""
ssp_ts.py: Construction and tabu search for the stable set problem.

The Stable Set Problem (SSP) is a combinatorial optimization problem
where: given a graph, find the maximum subset of nodes S such that
there are no edges between nodes in S.  This problem is equivalent to
finding the maximum clique in the complementary graph.

The SSP is well known for having very large plateaux, which cause many
search methods to fail.  This file contains a set of functions to
illustrate plateau search for this problem.

In these functions the solution stable set is represented by
  - sol -- set of nodes selected into the stable set
  - rmn -- remaining nodes (set of nodes not selected).
  - b[i] -- auxiliary information: number of nodes adjacent to i in the stable set.
Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""

LOG = False      # whether or not to print intermediate solutions
Infinity = 1.e10000
import random

from graphtools import *
from ssp_ts import evaluate

def possible_add(rmn,b):
    """Check which of the nodes in set 'rmn' can be added to
    the current stable set (i.e., which have no edges to nodes in
    the stable set, and thus have b[i] = 0).
    """
    return [i for i in rmn if b[i] == 0]


def one_edge(rmn,b):
    """Check which of the nodes in 'rmn' cause one conflict if added
    to the current stable set (i.e., which have exactly one edge to
    nodes in the stable set, and thus have b[i] = 1).
    """
    return [i for i in rmn if b[i] == 1]


def add_node(i, adj, sol, rmn, b):
    """Move node 'i' from 'rmn' into 'sol', and update 'b' accordingly."""
    sol.add(i)
    rmn.remove(i)
    for j in adj[i]:
        b[j] += 1


def expand_rand(add, sol, rmn, b, adj, maxiter, dummy=None):
    """Expand the current stable set ('sol') from randomly selected valid nodes.
    Use nodes in 'add' for the expansion; 'add' must be the subset
    of unselected nodes that may still be added to the stable set.
    """
    iteration = 0
    while add != [] and iteration<maxiter:
        iteration += 1
        i = random.choice(add)
        add_node(i, adj, sol, rmn, b)
        add.remove(i)
        add = possible_add(add,b)       # reduce list of possible additions
        # directly updating add is slower:
        # for j in list(add):
        #     if j in adj[i] or b[j] != 0:
        #         add.remove(j)
    return iteration


def expand_stat_deg(add, sol, rmn, b, adj, maxiter, degree):
    """Expand the current stable set ('sol'), selecting nodes with maximal
    degree on the initial graph.
    Use nodes in 'add' for the expansion; 'add' must be the subset
    of unselected nodes that may still be added to the stable set."""
    iteration = 0
    while add != [] and iteration<maxiter:
        iteration += 1
        min_deg = Infinity
        cand = []
        for i in add:
            if degree[i] < min_deg:
                cand = [i]
                min_deg = degree[i]
            elif degree[i] == min_deg:
                cand.append(i)
        i = random.choice(cand)
        add_node(i, adj, sol, rmn, b)
        add.remove(i)
        add = possible_add(add,b)       # reduce list of possible additions
    return iteration


def expand_dyn_deg(add, sol, rmn, b, adj, maxiter, dummy=None):
    """Expand the current stable set ('sol'), selecting nodes with maximal
    degree on 'add' (i.e., the subset of nodes that can still be added to
    the stable set).
    """
    iteration = 0
    degree = {}
    for i in add:
        degree[i] = len(set(add) & adj[i])
    while add != [] and iteration<maxiter:
        iteration += 1
        min_deg = Infinity
        cand = []
        for i in add:
            if degree[i] < min_deg:
                cand = [i]
                min_deg = degree[i]
            elif degree[i] == min_deg:
                cand.append(i)
        i = random.choice(cand)

        # update degree on nodes connected to i and in 'add'
        for j in set(add) & adj[i]:
            for k in set(add) & adj[j]:
                degree[k] -= 1

        # insert chosen node into 'sol'
        add_node(i, adj, sol, rmn, b)
        add.remove(i)
        add = possible_add(add,b)       # reduce list of possible additions

    return iteration


def iterated_expansion(nodes, adj, expand_fn, niterations, report=None):
    """Do repeated expansions until reaching 'niterations'.
    Expansion is done using the function 'expand_fn' coming as
    a parameter.

    Parameters:
     * nodes, adj -- graph information
     * expand_fn -- function to be used for the expansion
     * niterations -- maximum number of iterations
    """
    degree = [len(adj[i]) for i in nodes]   # used on 'expand_stat_deg'
    bestcard = 0
    iteration = 0
    while iteration < niterations:
        # starting solution
        rmn = set(nodes)
        sol = set([])
        b = [0 for i in nodes]
        add = list(nodes)       #  nodes for starting expansion
        iteration += expand_fn(add,sol,rmn,b,adj,niterations-iteration,degree)
        if len(sol) > bestcard:
            bestcard = len(sol)
            bestsol = list(sol)
            bestrmn = list(rmn)
            if report:
                report(bestcard, "sol: %r" % sol)
        if LOG:
            print 'iter:%d\t%d/%d' % (iteration, len(sol), bestcard)
    return bestsol,bestrmn,bestcard

        
def node_replace(v, sol, rmn, b, adj):
    """Node 'v' has been inserted in 'sol' and created one conflict.
    Remove the conflicting node (the one in 'sol' adjacent to 'v'),
    update 'b', and the check through which nodes expansion is possible.
    """
    connected = adj[v].intersection(sol)
    i = connected.pop()
    rmn.add(i)
    sol.remove(i)
    expand_nodes = []
    for j in adj[i]:
        b[j] -= 1
        if b[j] == 0 and j not in sol:
            expand_nodes.append(j)
    return expand_nodes


def plateau(sol, rmn, b, adj, maxiter):
    """Check nodes that create one conflict if inserted in the stable set;
    tentatively add them, and remove the conflict created.
    Exit whenever the stable set can be expanded (and return the
    subset of nodes usable for that).
    """
    iteration = 0
    while iteration < maxiter:
        one = one_edge(rmn,b)
        if one == []:
            return iteration, []
        v = random.choice(one)
        iteration += 2
        add_node(v, adj, sol, rmn, b)
        expand_nodes = node_replace(v, sol, rmn, b, adj)
        if expand_nodes != []:  # can expand, stop plateau search
            return iteration, expand_nodes

    return iteration, []


def multistart_local_search(nodes, adj, expand_fn, niterations, length, report=None):
    """Plateau search, using 'expand_fn' for the expansion.

    Parameters:
     * nodes, adj -- graph information
     * expand_fn -- function to be used for the expansion
     * niterations -- maximum number of iterations
     * length -- number of searches to do attempt on the each plateau
    """
    degree = [len(adj[i]) for i in nodes]   # used on 'expand_stat_deg'
    bestsol = []
    bestrmn = []
    bestcard = 0
    iteration = 0

    while iteration < niterations:

        if LOG:
            print "New plateau search"
        # select nodes for staring expansion
        add = list(nodes)       #  possible_add(rmn,b)
        # starting solution
        rmn = set(nodes)
        sol = set([])
        b = [0 for i in nodes]

        while add != []:
            iteration += expand_fn(add,sol,rmn,b,adj,niterations-iteration,degree)
            if LOG:
                print "expanding...", len(sol)
            if len(sol) > bestcard:
                bestcard = len(sol)
                bestsol = list(sol)
                bestrmn = list(rmn)
                if report:
                    report(bestcard, "sol: %r" % sol)
            maxiter = min(length, niterations - iteration)
            usediter, add = plateau(sol,rmn,b,adj,maxiter)
            iteration += usediter
            if LOG:
                print "plateau phase...", len(sol)
                print '\t\titer:%d\t%d/%d' % (iteration, len(sol), bestcard)

    return bestsol, bestrmn, bestcard



def expand_through(add, sol, rmn, expand_fn, b, adj, maxiter, degree):
    """Expand the current stable set ('sol').
    Initially use nodes in 'add' for the expansion;
    then, try with all the unselected nodes (those in 'rmn')."""
    # expand first through nodes sugested in 'add' only
    iteration = expand_fn(add, sol, rmn, b, adj, maxiter, degree)
    # check if expansion is possible through any node
    add = possible_add(rmn,b)
    return iteration + expand_fn(add, sol, rmn, b, adj, maxiter-iteration, degree)



def ltm_search(nodes, adj, expand_fn, niterations, length, report=None):
    """Plateau search including long-term memory,
    using 'expand_fn' for the expansion.

    Long-term memory 'ltm' keeps the number of times each node
    was used after successful expansions.
    
    Parameters:
     * nodes, adj -- graph information
     * expand_fn -- function to be used for the expansion
     * niterations -- maximum number of iterations
     * length -- number of searches to do attempt on the each plateau
    """
    degree = [len(adj[i]) for i in nodes]   # used on 'expand_stat_deg'
    bestsol = []
    bestrmn = []
    bestcard = 0
    iteration = 0

    ltm = [0 for i in nodes]
    while iteration < niterations:

        if LOG:
            print "New plateau search"
        # select nodes for staring expansion
        # starting solution
        rmn = set(nodes)
        sol = set([])
        b = [0 for i in nodes]

        # alternate between using intensification and diversification, using ltm
        if random.random() < 0.5:
            # # insert one of the most used nodes in stable set
            # maxsel = -1
            # for i in rmn:
            #     if ltm[i] > maxsel:
            #         maxsel = ltm[i]
            #         cand = [i]
            #     elif ltm[i] == maxsel:
            #         cand.append(i)
            # other possibility: insert one of the nodes from the best solution into the stable set
            if bestsol != []:
                cand = list(bestsol)
            else:
                cand = list(rmn)
        else:
            # insert one of the least used nodes in stable set
            minsel = Infinity
            for i in rmn:
                if ltm[i] < minsel:
                    minsel = ltm[i]
                    cand = [i]
                elif ltm[i] == minsel:
                    cand.append(i)

        # start expansion through intensification/diversification selected nodes
        add = cand

        while add != []:
            if LOG:
                print "expanding...", len(sol)
            iteration += expand_through(add,sol,rmn,expand_fn,b,adj,niterations-iteration,degree)
            for i in sol:
                ltm[i] += 1
            if len(sol) > bestcard:
                bestcard = len(sol)
                bestsol = list(sol)
                bestrmn = list(rmn)
                if report:
                    report(bestcard, "sol: %r" % sol)
            maxiter = min(length, niterations - iteration)
            usediter, add = plateau(sol,rmn,b,adj,maxiter)
            iteration += usediter
            if LOG:
                print "plateau phase...", len(sol)
                print '\t\titer:%d\t%d/%d' % (iteration, len(sol), bestcard)


    return bestsol, bestrmn, bestcard



def rm_node(i, adj, sol, rmn, b):
    """Move node 'i' from 'sol' into 'rmn', and update 'b' accordingly."""
    rmn.add(i)
    sol.remove(i)
    for j in adj[i]:
        b[j] -= 1



def hybrid(nodes, adj, niterations, length, report=None):
    """Plateau search, using a hybrid approach.
    
    The solution is partially kept after each plateau search:
    a node from the unselected 'rmn' set is chosen and added to
    the stable set, and then the conflicting nodes are removed.

    Plateau expansions are done through a randomly selected method,
    from random expansion, dynamic-degree-based expansion, or
    static-degree expansion.

    Long-term memory 'ltm' keeps the number of times each node
    was used after successful expansions.
    
    Parameters:
     * nodes, adj -- graph information
     * expand_fn -- function to be used for the expansion
     * niterations -- maximum number of iterations
     * length -- number of searches to do attempt on the each plateau
    """
    expand_fns = [expand_rand, expand_stat_deg, expand_dyn_deg]
    
    bestsol = []
    bestrmn = []
    bestcard = 0
    iteration = 0

    rmn = set(nodes)
    sol = set([])
    b = [0 for i in nodes]
    ltm = [0 for i in nodes]
    while iteration < niterations:

        if LOG:
            print "New plateau search"
        # alternate between using intensification and diversification, using ltm
        if random.random() < 0.5:
            # # insert one of the most used nodes in stable set
            # maxsel = -1
            # for i in rmn:
            #     if ltm[i] > maxsel:
            #         maxsel = ltm[i]
            #         cand = [i]
            #     elif ltm[i] == maxsel:
            #         cand.append(i)
            # add = random.choice(cand)
            # other possibility: pick a currently unselected node from best solution
            cand = rmn & set(bestsol)
            if len(cand) != 0:
                add = random.choice(list(cand))
            else:
                add = random.choice(list(rmn))
        else:
            # insert one of the least used nodes in stable set
            minsel = Infinity
            for i in rmn:
                if ltm[i] < minsel:
                    minsel = ltm[i]
                    cand = [i]
                elif ltm[i] == minsel:
                    cand.append(i)
            add = random.choice(cand)

        ### for some problems ltm causes losses in solution quality;
        ### in these cases (e.g. san400_0.7_1.clq), it is better to do
        # add = random.choice(rmn)

        # remove nodes on the set that would cause conflicts
        for i in sol & adj[add]:
            rm_node(i, adj, sol, rmn, b)
            iteration += 1

        add_node(add, adj, sol, rmn, b)
        iteration += 1

        add = possible_add(rmn,b)
        # expand_fn = random.choice(expand_fns)
        while add != []:
            expand_fn = random.choice(expand_fns)
            iteration += expand_through(add,sol,rmn,expand_fn,b,adj,niterations-iteration,degree)
            for i in sol:
                ltm[i] += 1
            if LOG:
                print "expanding...", len(sol)
            if len(sol) > bestcard:
                bestcard = len(sol)
                bestsol = list(sol)
                bestrmn = list(rmn)
                if report:
                    report(bestcard, "sol: %r" % sol)
            maxiter = min(length, niterations - iteration)
            usediter, add = plateau(sol,rmn,b,adj,maxiter)
            iteration += usediter 
            if LOG:
                print "plateau phase...", len(sol)
                print '\t\titer:%d\t%d/%d' % (iteration, len(sol), bestcard)

    return bestsol, bestrmn, bestcard




if __name__ == "__main__":
    """Plateau search for stable set problem: sample usage"""

    import sys
    if len(sys.argv) == 1:
        # rndseed = 1	   # uncomment for having always the same behavior
        # random.seed(rndseed)
        instance = "randomly created"
        nodes,edges = rnd_graph(6,.5)
        edges = complement(nodes,edges)
        adj = adjacent(nodes, edges)
        max_iterations = 1000
        length = len(nodes)/10
        method = "plateau_rand"
        method = random.choice([
            "exp_rand",
	    "exp_stat_deg",
	    "exp_dyn_deg",
	    "plateau_rand",
	    "plateau_stat_deg",
	    "plateau_dyn_deg",
	    "ltm_rand",
	    "ltm_stat_deg",
	    "ltm_dyn_deg",
	    "hybrid"
            ])
    elif len(sys.argv) == 6:
        method = sys.argv[1]
        instance = sys.argv[2]
        rndseed = int(sys.argv[3])
        random.seed(rndseed)
        length = float(sys.argv[4])
        max_iterations = int(sys.argv[5])
        print "reading file:", instance
        nodes,adj = read_compl_graph(instance)
    else:
        print "usage:", sys.argv[0], "method instance seed length iterations"
        print "where method is one of:"
        print "  * exp_rand"
        print "  * exp_stat_deg"
        print "  * exp_dyn_deg"
        print "  * plateau_rand"
        print "  * plateau_stat_deg"
        print "  * plateau_dyn_deg"
        print "  * ltm_rand"
        print "  * ltm_stat_deg"
        print "  * ltm_dyn_deg"
        print "  * hybrid"
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
    print "starting plateau search, method =", method
    if method == "exp_rand":
        sol,rmn,card = iterated_expansion(nodes, adj, expand_rand, max_iterations, report_sol)
    elif method == "exp_stat_deg":
        sol,rmn,card = iterated_expansion(nodes, adj, expand_stat_deg, max_iterations, report_sol)
    elif method == "exp_dyn_deg":
        sol,rmn,card = iterated_expansion(nodes, adj, expand_dyn_deg, max_iterations, report_sol)
    elif method == "plateau_rand":
        sol,rmn,card = multistart_local_search(nodes, adj, expand_rand, max_iterations, length, report_sol)
    elif method == "plateau_stat_deg":
        sol,rmn,card = multistart_local_search(nodes, adj, expand_stat_deg, max_iterations, length, report_sol)
    elif method == "plateau_dyn_deg":
        sol,rmn,card = multistart_local_search(nodes, adj, expand_dyn_deg, max_iterations, length, report_sol)
    elif method == "ltm_rand":
        sol,rmn,card = ltm_search(nodes, adj, expand_rand, max_iterations, length, report_sol)
    elif method == "ltm_stat_deg":
        sol,rmn,card = ltm_search(nodes, adj, expand_stat_deg, max_iterations, length, report_sol)
    elif method == "ltm_dyn_deg":
        sol,rmn,card = ltm_search(nodes, adj, expand_dyn_deg, max_iterations, length, report_sol)
    else:
        if method != "hybrid":
            print "unknown method; using hybrid version"
        degree = [len(adj[i]) for i in nodes]   # used on 'expand_sta_deg'
        sol,rmn,card = hybrid(nodes, adj, max_iterations, length, report_sol)

    # import profile
    # profile.run('sol,rmn,card = exp_rand(nodes, adj, max_iterations)')
    # profile.run('sol,rmn,card = exp_plateau(nodes, adj, max_iterations)')

    xcard, xinfeas, xb = evaluate(nodes, adj, sol)
    assert card == xcard and xinfeas == 0

    print
    print "final solution: z =", len(sol)
    print sorted(sol)
    print
