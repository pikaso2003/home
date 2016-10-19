#
#   Comments :
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

import matplotlib.pyplot as plt
from math import sqrt
from gurobipy import *
import pandas as pd
import numpy as np

plt.style.use('ggplot')


def markowitz_DC(I, sigma, r, alpha):
    model_TVaR = Model('Opt:Premium Const:TVaR')

    x = {}

    for i in range(I):
        x[i] = model_TVaR.addVar(vtype='C', lb=0.)
    model_TVaR.update()

    model_TVaR.addConstr(quicksum(r[i] * x[i] for i in range(I)) >= alpha)
    model_TVaR.addConstr(quicksum(x[i] for i in range(I)) == 1)

    # iteration for quicksum works well only when type of sigma is dictionary
    model_TVaR.setObjective(quicksum(x[i] * sigma[i, j] * x[j] for (i, j) in sigma), GRB.MINIMIZE)

    model_TVaR.update()

    model_TVaR.__data = x

    return model_TVaR


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
