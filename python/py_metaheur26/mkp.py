"""
mkp.py: Construction/oscillation/tabu search for the Multiple Knapsack Problem.

The Multiple Knapsack Problem (MKP) is a combinatorial optimization problem
where: given a set of items, each with a value (v_j) and a length in several
dimensions (a_ij), and a set of maximal values for each dimension (b_i), find
the subset of items that maximizes the total value, that fit in all the
dimensions:

This file contains a set of functions to illustrate construction and an
oscillation strategy.

Copyright (c) by Joao Pedro PEDROSO and Mikio KUBO, 2007
"""

LOG = False
import random
import math
Infinity = 1.e10000


def eval_and_sort(a, v, delta, allowed):
    """Evaluate/rate impact of all moves in 'allowed'.
    Parameters:
      a[i,j] - weight of item j, on dimension i (m x n  matrix of weights)
      v[j] - value of item j (objective, n-sized vector)
      delta[i] - capacity remaining for dimension i (rhs, m-sized vector)
      allowed - set of items currently allowed to be included
    Returns a list of items ordered by increasing value of rate.
    """
    cand = []
    constraints = range(len(delta))

    for j in allowed:
        rate = v[j]/(sum([float(a[i,j])/delta[i] for i in constraints if delta[i] > 0]) + \
                     sum([float(a[i,j])*(-delta[i]+2) for i in constraints if delta[i] <= 0]))

        cand.append((rate,j))
    cand.sort() # sort by ascending order with respect to rate
    return [j for (rate,j) in cand]     # extract indices in ordered list and return them


def add_critical(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report=None):
    """Check if adding some item could lead to an improvement on the best found solution.
    Parameters:
      a[i,j] - weight of item j, on dimension i (m x n  matrix of weights)
      v[j] - value of item j (objective, n-sized vector)
      sol - current set of selected items
      rmn - set of items allowed to be included
      delta[i] - capacity remaining for dimension i (rhs, m-sized vector)
      z - objective value for the current solution
      bestsol - current best found solution
      bestdelta - rhs for the current best found solution
      bestz - objective value for the current best found solution
    Returns a tuple (bestz, bestsol, bestdelta), consisting of:
    the best objective value found, and the corresponding solution and rhs.
    """
    constraints = range(len(delta))
    if z > bestz:
        bestsol, bestdelta, bestz = sorted(sol), list(delta), z
        if report: report(bestz)
    for j in rmn:
        if z + v[j] > bestz:
            for i in constraints:
                if a[i,j] > delta[i]:
                    break
            else:
                # solution is feasible, improved best found solution
                bestz = z + v[j]
                bestsol = sol | set([j])
                bestdelta = list(delta)
                for i in constraints:
                    bestdelta[i] -= a[i,j]
                if report: report(bestz, "*add*")
                assert check(a,b,v, bestsol, bestdelta, bestz)
    return sorted(bestsol), bestdelta, bestz



def del_critical(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report=None):
    """Check if removing some item makes sol feasible, and improves best found solution.
    Parameters, returns: as in add_critical.
    """
    violated = [i for i in range(len(delta)) if delta[i] < 0]
    constraints = range(len(delta))
    for j in sol:
        if z - v[j] > bestz:
            for i in violated:
                if a[i,j] + delta[i] < 0:
                    break
            else:
                # solution is feasible, improved best found solution
                bestz = z - v[j]
                bestsol = sol - set([j])
                bestdelta = list(delta)
                for i in constraints:
                    bestdelta[i] += a[i,j]
                    # assert bestdelta[i] >= 0
                if report: report(bestz, "*del*")
                continue

    return sorted(bestsol), bestdelta, bestz



def swap(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report=None):
    """Check if removing some item makes sol feasible, and improves best found solution.
    Parameters, returns: as in add_critical.
    """
    for j in sol:
        for jj in rmn:
            if z - v[j] + v[jj] > bestz:
                for ii in range(len(delta)):
                    if a[ii,j] - a[ii,jj] + delta[ii] < 0:
                        break
                else:
                    # solution is feasible, improved best found solution
                    bestz = z - v[j] + v[jj]
                    bestsol = (sol - set([j])) | set([jj])
                    bestdelta = list(delta)
                    for ii in range(len(delta)):
                        bestdelta[ii] -= a[ii,jj] - a[ii,j]
                        assert bestdelta[ii] >= 0
                    if report: report(bestz, "*swap*")
                    assert check(a,b,v, bestsol, bestdelta, bestz)

    return sorted(bestsol), bestdelta, bestz
    


def oscillation(a, v, sol, delta, z, niter, alpha=0, beta=1, report=None):
    """Try to improve 'sol' making oscillation into/from infeasible space.
    Parameters:
      a[i,j] - weight of item j, on dimension i (m x n  matrix of weights)
      v[j] - value of item j (objective, n-sized vector)
      sol - current set of selected items (assumed to be feasible)
      delta[i] - capacity remaining for dimension i (rhs, m-sized vector)
      z - objective value for the current solution
      niter - number of iterations allowed
      alpha - number of extra movements, after crossing feasible boundary
      beta - number of elements to include in candidate list
    Returns a tuple (bestz, bestsol, bestdelta), consisting of:
    the best objective value found, and the corresponding solution and rhs.
    """

    n = len(v)
    m = len(delta)
    items = set(range(n))
    constraints = range(m)
    feas = True         # assuming incoming solution is feasible
    bestsol, bestz, bestdelta = sorted(sol), z, list(delta)

    if LOG:
        print "initial objective\t", bestz

    cand_add = list(items - sol)        # candidates for adding (on the following step)
    rmn = items - sol   # remaining items (not in the solution)
    for it in range(niter):

        cand_drop = list(sol)        # candidates for dropping (on the following step)
        count = 0
        # add phase (making solution infeasible)
        while count <= random.randint(0,alpha) and cand_add != []:
            isorted = eval_and_sort(a, v, delta, cand_add)
            index = random.randint(1,beta)
            best = isorted[-index:]     # best items are at end of list
            item = random.choice(best)
            sol.add(item)
            rmn.remove(item)
            cand_add.remove(item)
            feas = True
            for i in constraints:
                delta[i] -= a[i,item]
                if delta[i] < 0:
                    feas = False
            z += v[item]
            if feas:
                if z > bestz:
                    bestsol, bestdelta, bestz = sorted(sol), list(delta), z
                    if report: report(bestz, "  * it:%d\t" % it)
            else:
                count += 1
                if count == 1:  # has just lost feasibility, try critical event removal/swaps
                    bestsol, bestdelta, bestz = \
                             del_critical(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report)
                    bestsol, bestdelta, bestz = \
                             swap(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report)

            if LOG: print "\tit %d: -> {%d}," % (it,item)
        if LOG: print "it %d, after adding: %g" % (it,z)
        
        # drop phase
        cand_add = list(items - sol)        # candidates for adding (on the following step)
        count = 0
        while count <= random.randint(0,alpha) and cand_drop != []:
            isorted = eval_and_sort(a, v, delta, cand_drop)
            index = random.randint(1,beta)
            worst = isorted[:index]     # worst items are at begin of list
            item = random.choice(worst)
            sol.remove(item)
            rmn.add(item)
            cand_drop.remove(item)
            feas = True
            for i in constraints:
                delta[i] += a[i,item]
                if delta[i] < 0:
                    feas = False
            z -= v[item]
            if LOG:     print "\tit %d: {} -> %d" % (it,item)

            if feas:
                count += 1
                if z > bestz:
                    bestsol, bestdelta, bestz = sorted(sol), list(delta), z
                    if report: report(bestz, "  * it:%d\t" % it)
                if count == 1:  # has just reached feasibility, try critical event additions/swaps
                    bestsol, bestdelta, bestz = \
                             add_critical(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report)
                    bestsol, bestdelta, bestz = \
                             swap(a, v, sol, rmn, delta, z, bestsol, bestdelta, bestz, report)
                    

        if LOG: print "it %d, after dropping: %g" % (it,z)
        
    if report: report(bestz, " * final solution *")
    return bestz, bestsol, bestdelta



#
# auxiliary functions: read data
#
def read_gk(filename):
    """Read data from a file in the format defined by Glover&Kochenberger.
    Returns a tuple (a,b,v) where
      a[i,j] - weight of item j, on dimension i (m x n  matrix of weights)
      b[i] - max.weight for dimension i (rhs, m-sized vector)
      v[j] - value of item j (objective, n-sized vector)
      """
    try:
        f = open(filename)
    except IOError:
        print "could not open file", filename
        exit(-1)

    data = f.read()
    f.close()

    data = data.strip()
    data = data.split()
    name = data.pop(0)

    data = map(int, data)
    n = data.pop(0)     # number of variables
    m = data.pop(0)     # number of constraints

    a, b, v = {}, [0]*m, [0]*n
    k = 0       # scanning position in the data list
    for j in range(n):
        v[j] = data[k]; k += 1  # cost
        for i in range(m):
            a[i,j] = data[k]; k += 1    # matrix

    for i in range(m):
        b[i] = data[k]; k += 1  # knapsack capacities (rhs)

    return a,b,v


def read_cb(filename):
    """Read data form a file in the format defined by Chu&Beasley.
    Returns a list of tuples [(a,b,v), ...], one tuple for each problem,
    where
      a[i,j] - weight of item j, on dimension i (m x n  matrix of weights)
      b[i] - max.weight for dimension i (rhs, m-sized vector)
      v[j] - value of item j (objective, n-sized vector)
      """
    try:
        f = open(filename)
    except IOError:
        print "could not open file", filename
        exit(-1)

    data = f.read()
    f.close()

    data = data.strip()
    data = data.split()
    data = map(int, data)

    nprobs = data.pop(0)        # there are 'nprobs' problems in each file

    k = 0       # scanning position in the data list
    all = []    # list with one (a,b,v) item for each problem defined in the file
    for p in range(nprobs):
        n = data[k]; k += 1     # number of variables
        m = data[k]; k += 1     # number of constraints
        opt = data[k]; k += 1   # optimal value (if known)

        a, b, v = {}, [0]*m, [0]*n
        for i in range(n):
            v[i] = data[k]; k += 1
        for j in range(m):
            for i in range(n):
                a[j,i] = data[k]; k += 1

        for j in range(m):
            b[j] = data[k]; k += 1

        all.append((a,b,v))
    return all


def random_data(m=10, n=100):
    """Generate instance data.
    Parameters:
      m - number of constraints
      n - number of variables
    Returns: as 'read_gk'
    """
    a, b, v = {}, [0]*m, [0]*n
    variables = range(n)
    constraints = range(m)
    for i in constraints:
        for j in variables:
            a[i,j] = int(1-1000*math.log(1-random.random(),2))
        b[i] = int(0.25 * sum([a[i,j] for j in variables]))

    for j in variables:
        v[j] = int(sum([a[i,j] for i in constraints])/m + 10*random.random())
    return (a,b,v)


def check(a,b,v, sol, delta, z):
    """checks if sol's objective is z, and if the remaining capacity is delta"""
    var = range(len(v))
    con = range(len(delta))
    if z != sum(v[j] for j in sol):
        print "z=%d, should be %d" % (z, sum(v[j] for j in sol))
        return False
    for i in con:
        if delta[i] != b[i] - sum(a[i,j] for j in sol):
            print "constraint %d: incorrect capacity %g (should be %g)" % (i, delta[i], sum(a[i,j] for j in sol))
            return False
        if delta[i] < 0:
            print "constraint %d: negative capacity" % i
        
    return True
    


if __name__ == "__main__":
    """Oscillation/tabu search for the Multiple Knapsack Problem: sample usage"""
    
    # function for printing best found solution when it is found
    from time import clock
    init = clock()
    def report_sol(obj,s=""):
        print "cpu:%g\tobj:%g\t%s" % \
              (clock(), obj, s)

    #
    # uncomment this for a simple test
    #
     
    # random.seed(0)	# uncomment for having always the same behavior
    # a,b,v = read_gk("INSTANCES/MKP/mk_gk01.txt")
    # a,b,v = read_gk("INSTANCES/MKP/test.txt")
    a,b,v = random_data(50,50)
    n = len(v)
    items = set(range(n))
     
    print "*** multiple knapsack problem ***"
    print

    print "instance randomly created"
    # create starting solution
    sol, delta, z = set([]), list(b), 0
    z, sol, delta = oscillation(a, v, sol, delta, z, niter=1, alpha=0, beta=1)
    assert check(a,b,v, sol, delta, z)
    print "greedy solution: z =", z
    print sol
    print

    # proceed with search
    print "starting oscillation"
    niter = 1000
    alpha = 1
    beta = 3
    z, sol, delta = oscillation(a, v, set(sol), delta, z, niter, alpha, beta, report=report_sol)
    assert check(a,b,v, sol, delta, z)
    print "final solution: z=", z
    print sol
    exit(0)
     

    # #
    # # uncomment this for a thorough test
    # #
    #  
    # # read all benchmark instances
    # all_instances = []
    # names = []
    # for p in range(9):
    #     chu = read_cb("INSTANCES/MKP/mknapcb%d.txt" % (p+1))
    #     for q in range(len(chu)):
    #         if q % 10 != 0:            # to select only a few instances
    #             continue
    #         a,b,v = chu[q]
    #         names.append("Chu & Beasley %d - %d.%d-%02d" % (p+1, len(b), len(v), q))
    #         all_instances.append((a,b,v))
    # for p in range(11):
    #     prob = "mk_gk%02d.txt" % (p+1)
    #     a,b,v = read_gk("INSTANCES/MKP/"+prob)
    #     names.append("Glover & Kochenberger %d (m=%d,n=%d)" % (p+1,len(b),len(v)))
    #     all_instances.append((a,b,v))
    #  
    # init = clock()
    # niter = 10000
    # alpha = 1
    # beta = 3
    # N = 10
    # for k in range(len(all_instances)):
    #     prob = names[k]
    #     a,b,v = all_instances[k]
    #     n = len(v)
    #     m = len(b)
    #     items = set(range(n))
    #     print prob, "\tn=", len(v), "\tm=", len(b)
    #  
    #     print "NEW OSCILLATION", niter, "ITER", N, "RUNS", "ALPHA=", alpha, "BETA=", beta
    #     start = clock()
    #     zlist = []
    #     for k in range(N):
    #         siter = clock()
    #         random.seed(k)
    #         sol, delta, z = set([]), list(b), 0
    #         z, sol, delta = oscillation(a, v, sol, delta, z, niter=1, alpha=0, beta=1)
    #         print "\titer", k, clock()-siter, "\tgreedy:\t", z,
    #         siter = clock()
    #         z, sol, delta = oscillation(a, v, set(sol), list(delta), z, niter, alpha, beta)
    #         assert check(a,b,v, sol, delta, z)
    #         print "\t->\t", z, clock()-siter
    #         zlist.append(z)
    #     print min(zlist), float(sum(zlist))/N, max(zlist), "time:", clock() - start
    #  
    # print "total time:", clock() - init
    # exit(0)

