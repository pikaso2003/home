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


from gurobipy import *
import pandas as pd
import numpy as np
import time
import os
from numpy import random
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import matplotlib.ticker as ptick
from sklearn.preprocessing import scale
from sklearn.cluster import KMeans
import pyOpt
import mpi4py
# from mpi4py import MPI
from pyOpt import Optimization
from pyOpt import ALPSO, ALHSO
import InsuranceTools.MC as ITMC
import InsuranceTools.YearTable as Ityt
from InsuranceTools.YearTable import YearTable
from InsuranceTools.DataConverter import pickle_read, pickle_write
import InsuranceTools.GA as ITGA
from multiprocessing import Process, Pool, cpu_count, current_process, Lock, Pipe

reload(ITMC)
reload(Ityt)
reload(ITGA)

mklist = ['pink', 'darkviolet', 'slategrey', 'moccasin', 'olivedrab', 'goldenrod', 'dodgerblue', 'coral',
          'yellowgreen',
          'skyblue', 'crimson']
#######################################################################################################################
#
#   todo                            parameter setting

work_dir_name = '1510testrun/'
accumulated_dir = './accumulated_data/' + work_dir_name  # all data is class type
accumulated_dir_risk_metric = './risk_metrics/' + work_dir_name
global_opt_result = './global_opt_result/' + work_dir_name
local_opt_result = './local_opt_result/' + work_dir_name
cycle = 50000
alpha = 0.99
beta = 0.998
MC_cycle = 1000
num_clusters = 5
global_const = [lambda w: np.array(w).sum > 0, lambda w: np.array(w).sum > 0]
weight_list = ['SJNKA', 'SJNKE', 'SJNKRe', 'SJNKIC', 'SJS']
w0 = [1., 1., 1., 1., 1.]
w_lower = [0.8, 0.8, 0.8, 0.8, 0.8]
w_upper = [1.2, 1.2, 1.2, 1.2, 1.2]
bnds = np.array([w_lower, w_upper])

Premium_list = []
Loss_list = []
Expense_list = []
for i in weight_list:
    Premium_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_P.pkl'))
    Loss_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_L.pkl'))
    Expense_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_E.pkl'))

I = len(weight_list)
Premium_list_gurobi = {}
Loss_list_gurobi = {}
Expense_list_gurobi = {}
for i in range(I):
    if i == 1 or i == 4:
        Premium_list_gurobi[i] = list(Premium_list[i].yt)
        Loss_list_gurobi[i] = list(Loss_list[i].yt)
        Expense_list_gurobi[i] = list(Expense_list[i].yt)
    else:
        Premium_list_gurobi[i] = list(Premium_list[i].yt)
        Loss_list_gurobi[i] = list(Loss_list[i].yt)
        Expense_list_gurobi[i] = list(Expense_list[i].yt)


# I : num of Biz line
#   realization_num : num of realization
def markowitz_TVaR(I, realization_num, default_TVaR, alpha, Premium_list_gurobi, Loss_list_gurobi, Expense_list_gurobi):
    def Aggregate(x, YT, realization_num):
        return quicksum(x * YT[i] for i in range(realization_num))

    model_TVaR = Model('Opt:Premium Const:TVaR')

    x = {}
    for i in range(I):
        x[i] = model_TVaR.addVar(vtype='C', lb=0.5, ub=2)

    u = {}
    for i in range(realization_num):
        u[i] = model_TVaR.addVar(vtype='C', lb=0.)

    VaR = model_TVaR.addVar(vtype='C', lb=0., name='VaR')

    model_TVaR.update()

    model_TVaR.addConstr(VaR + quicksum(u[i] for i in range(realization_num)) / (1 - alpha) == default_TVaR)
    for i in range(realization_num):
        model_TVaR.addConstr(quicksum(x[j] * Loss_list_gurobi[j][i] / realization_num for j in range(I)) - VaR / realization_num <= u[i])

    # iteration for quicksum works well only when type of sigma is dictionary
    model_TVaR.setObjective(quicksum(Aggregate(x[i], Premium_list_gurobi[i], realization_num) -
                                     Aggregate(x[i], Loss_list_gurobi[i], realization_num)
                                     - Aggregate(x[i], Expense_list_gurobi[i], realization_num) for i in range(I)) / realization_num, GRB.MAXIMIZE)

    model_TVaR.update()

    model_TVaR.__data = x
    model_TVaR.__data = VaR

    return model_TVaR


default_TVaR = Ityt.Uwg(ITMC.MCbase(Premium_list, w0, cycle), ITMC.MCbase(Loss_list, w0, cycle), ITMC.MCbase(Expense_list, w0, cycle)).xtvar(alpha)

model_TVaR = markowitz_TVaR(I, cycle, default_TVaR, alpha, Premium_list_gurobi, Loss_list_gurobi, Expense_list_gurobi)
model_TVaR.optimize()

status = model_TVaR.Status
if status == GRB.Status.UNBOUNDED or status == GRB.Status.INF_OR_UNBD:
    model_TVaR.setObjective(0, GRB.MAXIMIZE)
    model_TVaR.optimize()
    status = model_TVaR.Status
if status == GRB.Status.OPTIMAL:
    print 'UNbounded'
elif status == GRB.Status.INFEASIBLE:
    print 'Infeasible'
else:
    print 'Error : Solver finished with non-optimal status', status

print "Optimal value : ", model_TVaR.ObjVal
model_vars = model_TVaR.getVars()
for i in range(10):
    print model_vars[i]
