#
#   Comments :  study of second-order-cone problem
#
#   Arguments :
#
#   Return :
#
# ---------------------------------------------------------------------------------
#   Date        Developer       Action
#   Oct15       Hirayu
#
#
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import *
from gurobipy import *

mklist = ['pink', 'darkviolet', 'slategrey', 'moccasin', 'olivedrab', 'goldenrod', 'dodgerblue', 'coral', 'yellowgreen', 'skyblue', 'crimson']


# 2nd order cone constraints require dummy variable
# for checking semi-definitive
def weber(I, x, y, w):
    model = Model('weber')
    X, Y, z, xaux, yaux = {}, {}, {}, {}, {}
    X = model.addVar(vtype='I', lb=-GRB.INFINITY)
    Y = model.addVar(vtype='I', lb=-GRB.INFINITY)
    for i in I:
        z[i] = model.addVar(vtype='C')
        xaux[i] = model.addVar(vtype='I', lb=-GRB.INFINITY)
        yaux[i] = model.addVar(vtype='I', lb=-GRB.INFINITY)
    model.update()

    for i in I:
        model.addConstr(xaux[i] * xaux[i] + yaux[i] * yaux[i] <= z[i] * z[i])
        model.addConstr(xaux[i] == (x[i] - X))
        model.addConstr(yaux[i] == (y[i] - Y))

    model.setObjective(quicksum(w[i] * z[i] for i in I), GRB.MINIMIZE)

    model.update()
    model.__data = X, Y, z
    return model


def weber_solve():
    I, x, y, w = multidict({1: [24., 54., 2], 2: [60., 63., 1], 3: [1., 84., 2], 4: [23., 100., 3], 5: [84., 48., 4], 6: [15., 64., 5], 7: [52., 74., 4]})

    model1 = weber(I, x, y, w)
    model1.optimize()

    print 'Opt value : ', model1.ObjVal
    opt_var1 = model1.getVars()
    print 'Opt variable', opt_var1

    fig1, ax1 = plt.subplots(1, 1)
    for i in I:
        ax1.plot(x[i], y[i], 'o', ms=8, color=mklist[i], label=i)
    ax1.set_xlabel('x loc')
    ax1.set_ylabel('y loc')
    plt.legend()
    plt.tight_layout()
    ax1.plot(opt_var1[0].X, opt_var1[1].X, '+', ms=10, color='crimson', label='Optimized well point')
    plt.show()


# portfolio optimization
def markowitz(I, sigma, r, alpha):
    model = Model('Markowitz')
    x = {}
    for i in I:
        x[i] = model.addVar(vtype='C', lb=0.)
    model.update()

    model.addConstr(quicksum(r[i] * x[i] for i in I) >= alpha)
    model.addConstr(quicksum(x[i] for i in I) == 1)

    model.setObjective(quicksum(sigma[i] ** 2 * x[i] * x[i] for i in I), GRB.MINIMIZE)

    model.update()

    model.__data = x

    return model


def markowitz_solve():
    alpha = 1.05
    I, r, sigma = multidict({1: [1.01, 0.07], 2: [1.05, 0.09], 3: [1.08, 0.1], 4: [1.1, 0.2], 5: [1.2, 0.3]})
    model2 = markowitz(I, sigma, r, alpha)
    model2.optimize()

    print 'Opt value : ', sqrt(model2.ObjVal)
    print 'Opt share : '
    for i in model2.getVars():
        print i.VarName, i.X


# weber_solve()

def markowitz_DC(I, sigma, r, alpha):
    model_DC = Model('Markowitz_DC')

    x = {}

    for i in range(I):
        x[i] = model_DC.addVar(vtype='C', lb=0.)
    model_DC.update()

    model_DC.addConstr(quicksum(r[i] * x[i] for i in range(I)) >= alpha)
    model_DC.addConstr(quicksum(x[i] for i in range(I)) == 1)

    # iteration for quicksum works well only when type of sigma is dictionary
    model_DC.setObjective(quicksum(x[i] * sigma[i, j] * x[j] for (i, j) in sigma), GRB.MINIMIZE)

    model_DC.update()

    model_DC.__data = x

    return model_DC


def DC_optimizer(alpha_temp, flag):
    alpha = alpha_temp
    df = pd.read_excel('DC_optimization.xls')
    df = df.ix[:-5, :-1]

    portfolio = list(df)
    I = len(portfolio)

    df_cov = df.cov()
    array_cor = np.array(df_cov)
    dict_cor = {}
    for i in range(I):
        for j in range(I):
            dict_cor[i, j] = array_cor[i, j]

    df_mean = df.mean()
    list_mean = list(np.array(df_mean))

    model_DC = markowitz_DC(I, dict_cor, list_mean, alpha)
    model_DC.optimize()

    print 'Optimized risk : ', sqrt(model_DC.ObjVal)
    opt_share = []
    print 'Opt share : '
    for i in model_DC.getVars():
        print i.VarName, i.X
        opt_share.append(i.X)

    print df_cov
    print df_mean

    if flag == 1:
        fig, ax = plt.subplots(1, 1)
        ax.bar(range(len(opt_share)), opt_share, width=0.6, align='center')
        ax.set_xticks(np.arange(len(opt_share)))
        ax.set_xticklabels(portfolio, fontsize=6)
        ax.set_title('DC portfolio optimization')
        ax.set_xlim(-0.5, 13.5)
        ax.set_ylim(0, 1)
        ax.text(1, 0.6, 'Volatility : %f ' % sqrt(model_DC.ObjVal), fontsize=20)
        ax.text(1, 0.7, 'Return average : %f' % alpha, fontsize=20)
        ax.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        pass

    return sqrt(model_DC.ObjVal)


alpha = list(np.arange(0.1, 2.5, 0.1))
vol = []
for i in alpha:
    # print i
    vol.append(DC_optimizer(i, 0))

fig_1, ax_1 = plt.subplots(1, 1)
ax_1.plot(vol, alpha, '.', ms=5, color='crimson')
ax_1.set_xlabel('Volatility (%)')
ax_1.set_ylabel('Return (%)')
ax_1.set_title('Effective frontier', fontsize=20)
plt.show()
