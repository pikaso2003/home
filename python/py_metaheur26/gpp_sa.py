import random
import math

LOG = False     # whether or not to print intermediate solutions
from gpp_ts import construct

def evaluate(nodes, adj, sol, alpha):
    """Evaluate a solution.

    Input:
      - nodes, adj - the instance's graph
      - sol - the solution to evaluate
      - alpha - a penalty for imbalanced solutions

    Determines:
      - the cost of a solution, i.e., the number of edges going
        from one partition to the other;
      - bal - balance, i.e., the number of vertices in excess in partition 0
      - s[i] - number of edges adjacent to i in the same partition;
      - d[i] - number of edges adjacent to i in a different partition.
    """
    s = [0 for i in nodes]
    d = [0 for i in nodes]

    bal = 0
    for i in nodes:
        if sol[i] == 0:
            bal += 1
        else:
            bal -= 1
        for j in adj[i]:
            if sol[i] == sol[j]:
                s[i] += 1
            else:
                d[i] += 1

    cost = 0
    for i in nodes:
        cost += d[i]
    cost /= 2
    cost += alpha*abs(bal)
        
    return cost, bal, s, d


def find_move_rnd(n, sol, alpha, s, d, bal):
    """Find a random node to move from one part into the other."""
    
    istar = random.randint(0,n-1)

    part = sol[istar]
    if part == 0 and bal > 0 or part == 1 and bal < 0:    # moving into the small partition
        penalty = -2*alpha
    else:
        penalty = 2*alpha

    delta = s[istar] - d[istar] + penalty
    return istar,delta


def update_move(adj, sol, s, d, bal, istar):
    """Execute the chosen move."""

    part = sol[istar]
    sol[istar] = 1-part   # change the partition for the chosen node
    
    # update cost structure for node istar
    s[istar],d[istar] = d[istar],s[istar]       # istar swaped partitions, so swap s and d
    for j in adj[istar]:
        if sol[j] == part:
            s[j] -= 1
            d[j] += 1
        else:
            s[j] += 1
            d[j] -= 1

    # update balance information
    if part == 0:
        bal -= 2
    else:
        bal += 2
    return bal


def metropolis(T, delta):
    "Metropolis criterion for new configuration acceptance"
    if delta <= 0 or random.random() <= math.exp(-(delta)/T):
        return True
    else:
        return False


def estimate_temperature(n, sol, s, d, bal, X0):
    """Estimate initial temperature:
    check empirically based on a series of 'ntrials', that the estimated
    temperature leads to a rate 'X0'% acceptance:
    """

    ntrials = 10*len(sol)
    nsucc = 0
    deltaZ = 0.0
    for i in range(0,ntrials):
        istar,delta = find_move_rnd(n, sol, alpha, s, d, bal)
        if delta > 0:
            nsucc += 1
            deltaZ += delta

    if nsucc != 0:
        deltaZ /= nsucc

    # temperature approximation based on deltaZ
    # (average difference on the non-improving objectives)
    T = -deltaZ/math.log(X0)
    if LOG:
        print "initial acceptance rate:", X0
        print "initial temperature:", T
        print
    return T



def annealing(nodes, adj, sol, initprob, L, tempfactor, freezelim, minpercent, alpha, report):
    """Simulated annealing for the graph partitioning problem

    Parameters:
     * nodes, adj - graph definition
     * sol - initial solution
     * initprob - initial acceptance rate
     * L - number of tentatives at each temperature
     * tempfactor - cooling ratio
     * freezelim - max number of iterations with less that minpercent acceptances
     * minpercent - percentage of accepted moves for being not frozen
     * report - function used for output of best found solutions
     """
    n = len(nodes)
    z,bal,s,d = evaluate(nodes, adj, sol, alpha)
    if bal == 0:        # partition is balanced
        solstar,zstar = list(sol), z        # best solution found so far
        if report:
            report(zstar)

    T = estimate_temperature(n, sol, s, d, bal, initprob)
    if LOG:
        print "initial temp:", T, " current objective:", z, "(bal = %d)" % bal
        print "current solution:", sol
        print
        
    if T == 0:  # frozen, return imediately
        print "Could not determine initial temperature, giving up"
        exit(-1)
        


    nfrozen = 0 # count frozen iterations
    while nfrozen < freezelim:
        changes, trials = 0,0
        while trials < L:
            trials += 1
            istar,delta = find_move_rnd(n, sol, alpha, s, d, bal)
            if metropolis(T, delta):
                changes += 1

                if LOG:
                    print "accepted move on index %d, with delta=%g" % (istar,delta)

                bal = update_move(adj, sol, s, d, bal, istar)
                z += delta

                if bal == 0:    # partition is balanced
                    if z < zstar: # best solution found so far
                        solstar,zstar = list(sol),z
                        nfrozen = 0
                        if report:
                            report(zstar)

                if LOG:
                    print "temp:", T, " current objective:", z, "(bal = %d)" % bal
                    print "%d changes, frozen = %d/%d" % (changes, nfrozen+1, freezelim), \
                          "tentative = %d/%d" % (trials,L)
                    print "current solution:", sol
                    print

                    # # check if there was some error on cost evaluation:
                    # zp,balp,sp,dp = evaluate(nodes, adj, sol, alpha)
                    # assert balp == bal
                    # assert abs(zp-z) < 1.e-9    # floating point approx.equality

        T *= tempfactor # decrease temperature
        if float(changes)/trials < minpercent:
            nfrozen += 1

    if report:
        report(zstar)
    return solstar, zstar
            


if __name__ == "__main__":
    """Simulated Annealing for the Graph Partitioning Problem: sample usage"""
    
    from graphtools import *
    import sys
    if len(sys.argv) == 1:
        rndseed = 2
        random.seed(rndseed)
        instance = "randomly created"
        nodes,adj = rnd_adj_fast(6,.5)

        # david johnson's default values
        initprob = .4    # initial acceptance probability
        sizefactor = 16  # for det. # tentatives at each temp.
        tempfactor = .95 # cooling ratio
        freezelim = 5    # max number of iterations with less that minpercent acceptances
        minpercent = .02 # fraction of accepted moves for being not frozen
        alpha = .05      # imballance factor
        N = len(nodes)   # neighborhood size
        L = N*sizefactor # number of tentatives at current temperature 

    elif len(sys.argv) == 9:
        instance = sys.argv[1]
        rndseed = int(sys.argv[2])
        random.seed(rndseed)
        initprob = float(sys.argv[3])   # initial acceptance probability
        sizefactor = float(sys.argv[4]) # for det. # tentatives at each temp.
        tempfactor = float(sys.argv[5]) # cooling ratio
        freezelim = int(sys.argv[6])    # max # of it.with less that minpercent acceptances
        minpercent = float(sys.argv[7]) # percentage of accepted moves for being not frozen
        alpha = float(sys.argv[8])      # imballance factor

        nodes,adj = read_gpp_graph(instance)
        N = len(nodes)  # neighborhood size
        L = int(N*sizefactor)   # number of tentatives at current temperature

    else:
        print "usage:", sys.argv[0],
        print "instance seed initprob sizefactor tempfactor freezelim minpercent alpha"
        print "where:"
        print "initprob - initial acceptance probability"
        print "sizefactor - for det. # tentatives at each temp."
        print "tempfactor - cooling ratio"
        print "freezelim - max number of iterations with less that minpercent acceptances"
        print "minpercent - percentage of accepted moves for being not frozen"
        print "alpha - imballance factor"
        print 
        exit(-1)


    # function for printing best found solution when it is found
    from time import clock
    def report_sol(obj,s=""):
        print "cpu:%g\tobj:%g\t%s" % \
              (clock(), obj, s)

    print "*** graph partitioning problem ***"
    print

    print "instance", instance
    # print "nodes:", nodes
    # print "adjacencies", adj
    print "starting simulated annealing, parameters:"
    print "   initial acceptance probability", initprob
    print "   cooling ratio", tempfactor
    print "   # tentatives at each temp.", L
    print "   percentage of accepted moves for being not frozen", minpercent
    print "   max # of it.with less that minpercent acceptances", freezelim
    print "   imballance factor", alpha
    print
    sol = construct(nodes)        # starting solution
    z,bal,s,d = evaluate(nodes, adj, sol, alpha)
    print "initial partition: z =", z
    print sol
    print

    sol,z = annealing(nodes, adj, sol, initprob, L, tempfactor, freezelim, minpercent, alpha, report_sol)
    zp,bal,sp,dp = evaluate(nodes, adj, sol, alpha)
    assert abs(zp-z) < 1.e-9    # floating point approx.equality

    print
    print "final solution: z=", z
    print sol
