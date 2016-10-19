#
#   Comments : Gurobi book section 1
#
#   Arguments :
#
#   Return :
#
# ---------------------------------------------------------------------------------
#   Date        Developer       Action
#
#
#
from gurobipy import *
import numpy as np


# p10
def example1():
    model = Model()
    # arg : ( lower_limit, upper_limit, coeff_of_objfunc, var_type, name )
    x1 = model.addVar(0, 32, 15, GRB.INTEGER, 'x1')
    x2 = model.addVar(name='x2', vtype='I')
    x3 = model.addVar(ub=32, name='x3', vtype='I')
    model.update()
    model.addConstr(x1 + x2 + x3 == 32)
    model.addConstr(2 * x1 + 4 * x2 + 8 * x3 == 80)
    model.setObjective(x2 + x3)
    model.ModelSense = +1
    model.optimize()
    print 'Optimized Value : ', model.ObjVal
    print 'Optimized variables : '
    for i in model.getVars():
        print i.VaRName, i.X


# transportation problem
def example2():
    # I : customer number list
    # J : factory number list
    I, d = multidict({1: 80, 2: 270, 3: 250, 4: 160, 5: 180})
    J, M = multidict({1: 500, 2: 500, 3: 500})
    c = {(1, 1): 4, (1, 2): 6, (1, 3): 9, (2, 1): 5, (2, 2): 4, (2, 3): 7, (3, 1): 6, (3, 2): 3, (3, 3): 4,
         (4, 1): 8, (4, 2): 5, (4, 3): 3, (5, 1): 10, (5, 2): 8, (5, 3): 4, }
    model = Model()
    x = {}

    # Adding variable x[i,j]
    for i in I:
        for j in J:
            x[i, j] = model.addVar(vtype='C', name='x(%s,%s)' % (i, j))

    model.update()

    # Demand equation
    for i in I:
        model.addConstr(quicksum(x[i, j] for j in J) == d[i], name='Demand(%s)' % i)

    # Factory capacity
    for j in J:
        model.addConstr(quicksum(x[i, j] for i in I) <= M[j], name='Capacity(%s)' % j)

    model.setObjective(quicksum(c[i, j] * x[i, j] for (i, j) in x), GRB.MINIMIZE)

    model.optimize()

    print 'Optimal value : ', model.ObjVal
    EPS = 1e-6
    for (i, j) in x:
        if x[i, j].X > EPS:
            print 'sending quantity %10s from factory %3s to customer %3s' % (x[i, j].X, j, i)

    print 'Const. Name: Slack, Dual'
    for c in model.getConstrs():
        print '%s : %s , %s' % (c.ConstrName, c.Slack, c.Pi)


def example3():
    # product k = 1,2,3,4
    # customer i = 1,2,3,4,5
    # firm j = 1,2,3
    produce = {1: [2, 4], 2: [1, 2, 3], 3: [2, 3, 4]}
    d = {(1, 1): 80, (1, 2): 85, (1, 3): 300, (1, 4): 6,
         (2, 1): 270, (2, 2): 160, (2, 3): 400, (2, 4): 7,
         (3, 1): 250, (3, 2): 130, (3, 3): 350, (3, 4): 4,
         (4, 1): 160, (4, 2): 60, (4, 3): 200, (4, 4): 3,
         (5, 1): 180, (5, 2): 40, (5, 3): 150, (5, 4): 5}
    I = set([i for (i, k) in d])
    J, M = multidict({1: 3000, 2: 3000, 3: 3000})
    K, weight = multidict({1: 5, 2: 2, 3: 3, 4: 4})

    cost = {(1, 1): 4, (1, 2): 6, (1, 3): 9, (2, 1): 5, (2, 2): 4, (2, 3): 7,
            (3, 1): 6, (3, 2): 3, (3, 3): 4, (4, 1): 8, (4, 2): 5, (4, 3): 3, (5, 1): 10, (5, 2): 8, (5, 3): 4}

    c = {}
    for i in I:
        for j in J:
            for k in produce[j]:
                c[i, j, k] = cost[i, j] * weight[k]

    print ('( i, j, k) \t cost')
    print('-' * 20)
    for i in c:
        print i, '\t ', c[i]

    model = Model()
    x = {}
    for i, j, k in c:
        x[i, j, k] = model.addVar(vtype='C')
    model.update()

    for i in I:
        for k in K:
            model.addConstr(quicksum(x[i, j, k] for j in J if (i, j, k) in x) == d[i, k])

    for j in J:
        model.addConstr(quicksum(x[i, j, k] for (i, j2, k) in x if j2 == j) <= M[j])

    model.setObjective(quicksum(c[i, j, k] * x[i, j, k] for (i, j, k) in x), sense=GRB.MINIMIZE)

    model.optimize()

    print 'Optimal value : ', model.ObjVal


def example4():
    # a(i,k) : nutrition k of material i
    # i : material 1,2,3,4
    # k : nutrition 1,2,3
    a = {(1, 1): .25, (1, 2): .15, (1, 3): .30, (2, 1): .30, (2, 2): .30, (2, 3): .10, (3, 1): .15, (3, 2): .65,
         (3, 3): .05,
         (4, 1): .10, (4, 2): .05, (4, 3): .85}
    I, p = multidict({1: 5, 2: 6, 3: 8, 4: 20})
    K, LB, UB = multidict({1: [.1, .2], 2: [.0, .35], 3: [.45, 1.0]})

    model = Model()
    x = {}
    for i in I:
        x[i] = model.addVar()
    model.update()

    model.addConstr(quicksum(x[i] for i in I) == 1.)
    for k in K:
        model.addConstr(quicksum(a[i, k] * x[i] for i in I) <= UB[k])
        model.addConstr(quicksum(a[i, k] * x[i] for i in I) >= LB[k])
    model.setObjective(quicksum(p[i] * x[i] for i in I), GRB.MINIMIZE)
    model.optimize()
    for i in I:
        print i, x[i].X


# multi-constrained knapsack problem
def example5():
    # J : number of bear
    # v : value of bear
    # a : coefficients of linear constraints
    # I : number of constraints
    # b : limit value of linear constraints

    def knapsack():
        J, v = multidict({1: 16., 2: 19., 3: 23., 4: 28.})
        a = {(1, 1): 2, (1, 2): 3, (1, 3): 4, (1, 4): 5,
             (2, 1): 3000, (2, 2): 3500, (2, 3): 5100, (2, 4): 7200}
        I, b = multidict({1: 7, 2: 10000})
        return I, J, v, a, b

    def mkp(I, J, v, a, b):
        model = Model()
        x = {}
        for j in J:
            x[j] = model.addVar(vtype='B', name='x_%d' % j)
        model.update()
        for i in I:
            model.addConstr(quicksum(a[i, j] * x[j] for j in J) <= b[i])
        model.setObjective(quicksum(v[j] * x[j] for j in J), GRB.MAXIMIZE)
        return model

    I, J, v, a, b = knapsack()
    model = mkp(I, J, v, a, b)
    model.update()
    model.write('mkp.lp')
    model.optimize()
    print 'Optimal value : ', model.ObjVal
    for v in model.getVars():
        print v.VarName, v.X
    status = model.Status
    print status


example5()
