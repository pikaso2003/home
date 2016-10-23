import random
from sys import maxint
from graphtools import *
Infinity = 1.e10000
LOG = False	# whether or not to print intermediate solutions

#
# utility functions
#
def mk_rnd_data(n, scale=10):
    """Make data for a random problem of size 'n'."""
    f = {}      # for holding n x n flow matrix
    d = {}      # for holding n x n distance matrix
    
    for i in range(n):
        f[i,i] = 0
        d[i,i] = 0
    for i in range(n-1):
        for j in range(i+1,n):
            f[i,j] = int(random.random() * scale)
            f[j,i] = f[i,j]
            d[i,j] = int(random.random() * scale)
            d[j,i] = d[i,j]

    return n,f,d


def read_qap(filename):
    """Read data for a QAP problem from file in QAPLIB format."""
    try:
        if len(filename)>3 and filename[-3:] == ".gz":  # file compressed with gzip
            import gzip
            f = gzip.open(filename, "rb")
        else:   # usual, uncompressed file
            f = open(filename)
    except IOError:
        print "could not open file", filename
        exit(-1)

    data = f.read()
    f.close()

    try:
        pass
        data = data.split()
        n = int(data.pop(0))
        f = {}  # for n times n flow matrix
        d = {}  # for n times n distance matrix
        for i in range(n):
            for j in range(n):
                f[i,j] = int(data.pop(0))
        for i in range(n):
            for j in range(n):
                d[i,j] = int(data.pop(0))
    except IndexError:
        print "inconsistent data on QAP file", filename
        exit(-1)
    return n, f, d


#
# solution evaluation
#
def evaluate__(n,f,d,pi):
    """Evaluate solution 'pi' from scratch."""
    cost = 0
    for i in range(n-1):
        for j in range(i+1,n):
            cost += f[i,j] * d[pi[i],pi[j]]
    return cost*2

def evaluate(n,f,d,pi):
    """Evaluate solution 'pi' and create additional cost information for incremental evaluation."""
    delta = {}
    for i in range(n):
        for j in range(n):
            delta[i,j] = 0
            for k in range(n):
                delta[i,j] += f[i,k] * d[j,pi[k]]
    cost = 0
    for i in range(n):
        cost += delta[i,pi[i]]
    return cost,delta


#
#  qap solving 
#
def construct(n,f,d):
    """Random construction."""
    pi = range(n)
    random.shuffle(pi)
    return pi


def diversify(pi):
    """remove part of the solution, random re-construct it"""
    n = len(pi)
    missing = set(pi)

    start = int(random.random()*n)
    ind = range(n)
    random.shuffle(ind)
    for ii in range(start):
        i = ind[ii]
        missing.remove(pi[i])

    missing = list(missing)
    random.shuffle(missing)
    for ii in range(start,n):
        i = ind[ii]
        pi[i] = missing.pop()
    return pi

   
def find_move(n,f,d,pi,delta,tabu,iteration):
    """Find and return best non-tabu move."""
    minmove = Infinity
    istar,jstar = None,None
    for i in range(n-1):
        for j in range(i+1,n):
            if tabu[i,pi[j]] > iteration or\
               tabu[j,pi[i]] > iteration:
                continue

            move = delta[j, pi[i]] - delta[j, pi[j]] \
                     + delta[i, pi[j]] - delta[i, pi[i]] \
                     + 2 * f[i, j] * d[pi[i], pi[j]]

            if move < minmove:
                minmove = move
                istar = i
                jstar = j
                # print "\t\t%d,%d\t%d:%f" % (i,j,mindelta,minmove)

    if istar != None:
        return istar, jstar, minmove*2

    print "blocked, no non-tabu move"
    # clean tabu list
    for i in range(n):
        for j in range(n):
            tabu[i,j] = 0
    return find_move(n,f,d,pi,delta,tabu,iteration)


def tabu_search(n,f,d,max_iter,length,report=None):
    """Construct a random solution, and do 'max_iter' tabu search iterations on it."""
    tabulen = length
    tabu = {}
    for i in range(n):
        for j in range(n):
            tabu[i,j] = 0
    pi = construct(n,f,d)
    cost,delta = evaluate(n,f,d,pi)
    bestcost = cost

    if LOG: print "iteration", 0, "\tcost =", cost, ", best =", bestcost # , "\t", bestsol
    for it in range(max_iter):
        # search neighborhood
        istar, jstar, mindelta = find_move(n,f,d,pi,delta,tabu,it)

        # update cost info
        cost += mindelta
        for i in range(n):
            for j in range(n):
                delta[i,j] += (f[i,jstar] - f[i,istar]) * (d[j,pi[istar]] - d[j,pi[jstar]])

        # update tabu info
        tabu[istar, pi[istar]] = it + tabulen
        tabu[jstar, pi[jstar]] = it + tabulen

        # move
        pi[istar],pi[jstar] = pi[jstar],pi[istar]

        if cost < bestcost:
            bestcost = cost
            bestsol = list(pi)
            if report:
                report(bestcost, "it:%d"%it)
        if LOG: print "iteration", it+1, "\tcost =", cost, "/ best =", bestcost # , "\t", bestsol

    if report:
        report(bestcost, "it:%d"%it)

    # check if there was some error on cost evaluation:
    xcost, xdelta = evaluate(n,f,d,pi)
    assert xcost == cost

    return bestsol, bestcost



if __name__ == "__main__":
    """Tabu search for the Quadratic Assignment Problem: sample usage."""
    import sys
    if len(sys.argv) == 1:
        # rndseed = 1	# uncomment for having always the same behavior
        # random.seed(rndseed)
        instance = "randomly created"
        n,f,d = mk_rnd_data(5)
        tabulen = 4
        max_iterations = 1000
        ltmfactor = 0.
    elif len(sys.argv) == 5:
        instance = sys.argv[1]
        rndseed = int(sys.argv[2])
        random.seed(rndseed)
        tabulen = float(sys.argv[3])
        max_iterations = int(sys.argv[4])
        n,f,d = read_qap(instance)
        print "read file:", instance
    else:
        print "usage:", sys.argv[0], "instance seed tabulength iterations"
        exit(-1)

    # check if the instance is symmetric, otherwise exit
    try:
        for i in range(n):
            assert f[i,i] == 0 and d[i,i] == 0
        for i in range(n-1):
            for j in range(i+1,n):
                assert f[i,j] == f[j,i] and d[i,j] == d[j,i]
    except AssertionError:
        print "instance is not symmetric, cannot use this program"
        exit(-1)

    # print "f=\n", f
    # print "d=\n", d

    # function for printing best found solution when it is found
    from time import clock
    init_cpu = clock()
    def report_sol(obj,s=""):
        print "cpu:%g\tobj:%g\t%s" % \
              (clock() - init_cpu, obj, s)

    
    print "*** quadratic assignment problem ***"
    print

    print "instance:", instance
    print "n=", n
    print "flow:"
    for i in range(n):
        print [f[i,j] for j in range(n)]
    print "distance:"
    for i in range(n):
        print [d[i,j] for j in range(n)]
    print

    print "starting tabu search"
    pi,cost = tabu_search(n,f,d,max_iterations,tabulen,report_sol)

    print "final solution: z =", cost
    print pi
    
    c1 = evaluate__(n,f,d,pi)
    assert c1 == cost
