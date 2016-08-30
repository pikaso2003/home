import time
import os
import numpy as np
import pandas as pd
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

work_dir_name = '1512macro/'
accumulated_dir = './accumulated_data/' + work_dir_name  # all data is class type
accumulated_dir_risk_metric = './risk_metrics/' + work_dir_name
global_opt_result = './global_opt_result/' + work_dir_name
local_opt_result = './local_opt_result/' + work_dir_name
cycle = 100000
alpha = 0.995  # 200yr --> 0.995      100yr --> 0.99
beta = 0.998
MC_cycle = 2000
num_clusters = 5
global_const = [lambda w: ITMC.MCbase(USEQ_list, w, cycle).tvar(alpha) / SGO_USEQ_limit < 1.1,
                lambda w: ITMC.MCbase(USWS_list, w, cycle).tvar(alpha) / SGO_USWS_limit < 1.1,
                lambda w: ITMC.MCbase(EUWS_list, w, cycle).tvar(alpha) / SGO_EUWS_limit < 1.1,
                lambda w: ITMC.MCbase(JPWS_list, w, cycle).tvar(alpha) / SGO_JPWS_limit < 1.1,
                lambda w: ITMC.MCbase(JPEQ_list, w, cycle).tvar(alpha) / SGO_JPEQ_limit < 1.1,
                lambda w: ITMC.MCbase(RoW_list, w, cycle).tvar(alpha) / SGO_RoW_limit < 1.1
                ]
weight_list = list(pd.read_table('weight.txt').columns)  # setting of Optimized Variable's name
w_initial = [1.] * len(weight_list)
w_lower = list(pd.read_table('weight.txt').ix[0, :])
w_upper = list(pd.read_table('weight.txt').ix[1, :])
bnds = np.array([w_lower, w_upper])

Premium_list = []
Loss_list = []
Expense_list = []
for i in weight_list:
    Premium_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_P.pkl'))
    Loss_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_L.pkl'))
    Expense_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_E.pkl'))

USEQ_list = []
USWS_list = []
EUWS_list = []
JPWS_list = []
JPEQ_list = []
RoW_list = []
for i in weight_list:
    USEQ_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_USEQ.pkl'))
    USWS_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_USWS.pkl'))
    EUWS_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_EUWS.pkl'))
    JPWS_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_JPWS.pkl'))
    JPEQ_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_JPEQ.pkl'))
    RoW_list.append(pickle_read(accumulated_dir + 'YearTable_class/' + i + '_RoW.pkl'))

SGO_USEQ_limit = ITMC.MCbase(USEQ_list, w_initial, cycle).tvar(alpha)
SGO_USWS_limit = ITMC.MCbase(USWS_list, w_initial, cycle).tvar(alpha)
SGO_EUWS_limit = ITMC.MCbase(EUWS_list, w_initial, cycle).tvar(alpha)
SGO_JPWS_limit = ITMC.MCbase(JPWS_list, w_initial, cycle).tvar(alpha)
SGO_JPEQ_limit = ITMC.MCbase(JPEQ_list, w_initial, cycle).tvar(alpha)
SGO_RoW_limit = ITMC.MCbase(RoW_list, w_initial, cycle).tvar(alpha)

### tuple format
### cons = ({'type': 'ineq', 'fun': lambda x:  x[0] - 2 * x[1] + 2},
###...         {'type': 'ineq', 'fun': lambda x: -x[0] - 2 * x[1] + 6},
###...         {'type': 'ineq', 'fun': lambda x: -x[0] + 2 * x[1] + 2})
"""local_const = ({'type': 'ineq', 'fun': lambda w: -ITMC.MCbase(USEQ_list, w, cycle).tvar(alpha) + SGO_USEQ_limit},
               {'type': 'ineq', 'fun': lambda w: -ITMC.MCbase(USWS_list, w, cycle).tvar(alpha) + SGO_USWS_limit},
               {'type': 'ineq', 'fun': lambda w: -ITMC.MCbase(EUWS_list, w, cycle).tvar(alpha) + SGO_EUWS_limit},
               {'type': 'ineq', 'fun': lambda w: -ITMC.MCbase(JPWS_list, w, cycle).tvar(alpha) + SGO_JPWS_limit},
               {'type': 'ineq', 'fun': lambda w: -ITMC.MCbase(JPEQ_list, w, cycle).tvar(alpha) + SGO_JPEQ_limit},
               {'type': 'ineq', 'fun': lambda w: -ITMC.MCbase(RoW_list, w, cycle).tvar(alpha) + SGO_RoW_limit})"""
local_const = ({'type': 'eq', 'fun': lambda w: -ITMC.MCbase(USEQ_list, w, cycle).tvar(alpha) + SGO_USEQ_limit},
               {'type': 'eq', 'fun': lambda w: -ITMC.MCbase(USWS_list, w, cycle).tvar(alpha) + SGO_USWS_limit},
               {'type': 'eq', 'fun': lambda w: -ITMC.MCbase(EUWS_list, w, cycle).tvar(alpha) + SGO_EUWS_limit},
               {'type': 'eq', 'fun': lambda w: -ITMC.MCbase(JPWS_list, w, cycle).tvar(alpha) + SGO_JPWS_limit},
               {'type': 'eq', 'fun': lambda w: -ITMC.MCbase(JPEQ_list, w, cycle).tvar(alpha) + SGO_JPEQ_limit},
               {'type': 'eq', 'fun': lambda w: -ITMC.MCbase(RoW_list, w, cycle).tvar(alpha) + SGO_RoW_limit})


# CUS, DF, NAF, TPEx, SINGA, TPR, UKS, GS, TPQS, SCRE, SJNKA_LP, SJNKE, SompoOO
total_capital = 601669. * 1000
Risk_charge = [967, 3411, 3598, 12481, 957, 1162, 7153, 16894, 6128, 4773, 993, 2391, 6406]
Risk_charge = np.array(Risk_charge) * 1000

Cat_AAL_coeff = 0.9353900
NonCat_AAL_coeff = 0.9635669
NetPremium_coeff = 1.0470630


def obj_func(w1):
    return (Ityt.Uwg(ITMC.MCbase(Premium_list, w1, cycle), ITMC.MCbase(Loss_list, w1, cycle),
                     ITMC.MCbase(Expense_list, w1, cycle)).uwg_mean() - (Risk_charge * np.array(w1)).sum()) * -1. / total_capital


i_SLSQP = 1


def callback_func(w):
    plt.ion()
    global i_SLSQP
    axes[0].plot(i_SLSQP, -obj_func(w), 'ro', ms=3)
    axes[0].set_xlabel('Simulation cycle')
    axes[0].grid(True)
    axes[1].clear()
    axes[1].grid(True)
    axes[1].set_xticks(range(len(weight_list)))
    axes[1].set_xticklabels(weight_list, fontsize=8)
    axes[1].set_ylabel('Biz shares')
    axes[1].set_ylim(0, 1.30)
    axes[1].bar(range(len(w)), w)
    axes[1].set_xticks(range(len(weight_list)))
    axes[1].set_xticklabels(weight_list, fontsize=8)
    plt.draw()
    i_SLSQP += 1
    print('%i th iteration : %f \n' % (i_SLSQP, obj_func(w)))


#######################################################################################################
#       Particle Swarm Optimization
#       ALPSO
#######################################################################################################
alpso_cycle = 10  # input more than 2 value at least

w_initial = [1.] * 117
alpso_weight = [0.] * 7 + [0.2] * 110


# alpso_penalty = 1.


def obj_func_PSO(w1):
    w1 = list(np.array(w1) * np.array(alpso_weight) + 1.)
    f = Ityt.Uwg(ITMC.MCbase(Premium_list, w1, cycle), ITMC.MCbase(Loss_list, w1, cycle),
                 ITMC.MCbase(Expense_list, w1, cycle)).rorac(alpha) * -1.
    g = [0.] * 2
    g[0] = Ityt.Uwg(ITMC.MCbase(Premium_list, w1, cycle), ITMC.MCbase(Loss_list, w1, cycle),
                    ITMC.MCbase(Expense_list, w1, cycle)).xtvar(alpha) - Ityt.Uwg(
        ITMC.MCbase(Premium_list, w_initial, cycle), ITMC.MCbase(Loss_list, w_initial, cycle),
        ITMC.MCbase(Expense_list, w_initial, cycle)).xtvar(alpha)
    g[1] = 0.9 * Ityt.Uwg(ITMC.MCbase(Premium_list, w_initial, cycle), ITMC.MCbase(Loss_list, w_initial, cycle),
                          ITMC.MCbase(Expense_list, w_initial, cycle)).xtvar(alpha) - Ityt.Uwg(
        ITMC.MCbase(Premium_list, w1, cycle), ITMC.MCbase(Loss_list, w1, cycle),
        ITMC.MCbase(Expense_list, w1, cycle)).xtvar(alpha)
    fail = 0
    print 'obj_value : ', f, ' variable : ', w1
    print 'penalty(negative value is valid) : ', g[0], g[1]
    return f, g, fail


opt_prob = Optimization('Insurance Portfolio Optimization', obj_func_PSO)
# There is a problem in variable type 'Discrete'
wlen = len(w_lower)
for w_low, w_high, i in zip(w_lower, w_upper, range(wlen)):
    opt_prob.addVar(weight_list[i], type='i', value=0., lower=-1., upper=1.)
opt_prob.addObj('f')
opt_prob.addConGroup('g', 2, type='i')


# todo : ALPSO parmetor setting
def alpso_wrapper(opt_prob):
    alpso = ALPSO()
    alpso.setOption('SwarmSize', 10)  # default 40 -> 150
    alpso.setOption('maxOuterIter', 5)  # defualt 200
    # alpso.setOption('rinit', 1.)  # penalty factor
    alpso.setOption('fileout', 0)
    alpso.setOption('stopCriteria', 0)
    return alpso(opt_prob)


def alpso_func(opt_prob):
    temp = alpso(opt_prob)
    print opt_prob.solution(0)
    opt_prob.delSol(0)
    return temp[0]


def pipefunc(conn, alpso_func, opt_prob):
    conn.send(alpso_func(opt_prob))
    conn.close()


#######################################################################################################
#
#                                       Harmonic Optimization
#                                                                 ALHSO
#
#######################################################################################################
alhso_n = 30


#######################################################################################################
#
#                                              GA parameter
#
#######################################################################################################
n_pop = 200
cxpb = 0.7  # crossover prob
indpb = 0.5  # mutation prob for each element
mutpb = 0.5  # mutation prob whether mutation occurs or not
ngen = 50  # number of generation for calc
feasible = 100.  #
adjuster = 1e-10
### Theoretical and Numerical Constraint-Handling Techniques used with Evolutionary Algorithms
### Coello Coello 2002
### 2.2 Dynamic Penalties   p7
### coefficients of Joines and Houck's Dynamic penalties
C_JandH = 0.5
alpha_JandH = 1.
beta_JandH = 1.


# In GA algo, applying maximazation method
# todo NOTE : DO NOT FORGET ' , ' mark
def GA_const_JandH(w, C_JandH, alpha_JandH, ngen_count, feasible, adjuster):
    xtvar_check = Ityt.Uwg(ITMC.MCbase(Premium_list, w_initial, cycle), ITMC.MCbase(Loss_list, w_initial, cycle),
                           ITMC.MCbase(Expense_list, w_initial, cycle)).xtvar(alpha) - Ityt.Uwg(
        ITMC.MCbase(Premium_list, w, cycle), ITMC.MCbase(Loss_list, w, cycle),
        ITMC.MCbase(Expense_list, w, cycle)).xtvar(alpha)
    if abs(xtvar_check) < feasible:
        feasible_ret = 0
    else:
        feasible_ret = (C_JandH * ngen_count) ** alpha_JandH * abs(xtvar_check)

    return feasible_ret * adjuster


def obj_func_ga(w1, ngen_count):
    return Ityt.Uwg(ITMC.MCbase(Premium_list, w1, cycle), ITMC.MCbase(Loss_list, w1, cycle),
                    ITMC.MCbase(Expense_list, w1, cycle)).rorac(alpha) - GA_const_JandH(w1, C_JandH,
                                                                                        alpha_JandH,
                                                                                        ngen_count, feasible,
                                                                                        adjuster),


# no constraint for initial generation
def obj_func_ga_initial(w1):
    return Ityt.Uwg(ITMC.MCbase(Premium_list, w1, cycle), ITMC.MCbase(Loss_list, w1, cycle),
                    ITMC.MCbase(Expense_list, w1, cycle)).rorac(alpha),


#
#                   End of parameter setting
#######################################################################################################


if __name__ == '__main__':
    print('*' * 100)
    print('Select code number \n (1) : \t Global Optimization \n (2) : \t Local Optimization \n (Others) : Exit')
    print('Input : '),
    selector1 = raw_input()
    if selector1 == '1':
        print('*' * 100)
        print(
            'Select Global Optimization Method \n (1) : MonteCarlo \n (2) : Genetic Algorithm (Not Recommended) \n (3) : Particle Swarm Optimization \n (4) : Harmony Search '
            'Optimization (Not Recommended)')
        print('Input : '),
        selector2 = raw_input()

        if selector2 == '1':
            print('-' * 100)
            print('Global Optimization by MonteCarlo Method')
            print('*' * 100)
            print('\n')

            """
            Monte Carlo main routine
            """
            fig, axes = plt.subplots(1, 2)
            axes[0].xaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))
            axes[0].yaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))
            axes[0].ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
            axes[1].tick_params(labelsize=9)
            axes[1].xaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))
            axes[1].yaxis.set_major_formatter(ptick.ScalarFormatter(useMathText=True))
            axes[1].ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
            axes[1].tick_params(labelsize=9)
            result_w = []  # result of allocation
            result_uwg = []  # Uwg class list
            result_uwg_mean = []
            result_xtvar = []

            for i in range(MC_cycle):
                w = ITMC.weight_gen(w_lower, w_upper)
                if ITMC.constraints(global_const, w):
                    result_w.append(w)

                    result_uwg.append(
                        Ityt.Uwg(ITMC.MCbase(Premium_list, w, cycle), ITMC.MCbase(Loss_list, w, cycle),
                                 ITMC.MCbase(Expense_list, w, cycle)))
                    uwg_mean_temp = Ityt.Uwg(ITMC.MCbase(Premium_list, w, cycle), ITMC.MCbase(Loss_list, w, cycle), ITMC.MCbase(Expense_list, w, cycle)).uwg_mean()
                    xtvar_temp = Ityt.peril_allocation(Loss_list, w, cycle).xtvar(alpha)

                    xtvar_temp = Ityt.peril_allocation(Loss_list, w, cycle).xtvar(alpha)
                    result_uwg_mean.append(uwg_mean_temp)
                    result_xtvar.append(xtvar_temp)
                    print('%d th \t uwg_mean : %d \t\t XTVaR \t : %d' % (i + 1, int(uwg_mean_temp), int(xtvar_temp)))
                    axes[0].plot(uwg_mean_temp, xtvar_temp, 'o', ms=4, color=mklist[0])
                else:
                    print('\n data is in the infeasible region . \n')

            glabel = ITMC.clustering(result_uwg_mean, result_xtvar, num_clusters, result_w, global_opt_result)
            for i in range(num_clusters):
                axes[1].plot(np.array(result_uwg_mean)[glabel == i], np.array(result_xtvar)[glabel == i], 'o',
                             color=mklist[i + 1],
                             ms=4)
            plt.tight_layout()
            plt.show()

        elif selector2 == '2':
            """
            GA main routine
            """
            print('-' * 100)
            print('Global Optimization by Genetic Algorithm')
            ret_weight = ITGA.ga_main(bnds, n_pop, obj_func_ga, obj_func_ga_initial, cxpb, indpb, mutpb, ngen)
            print('-' * 100)
            print('Genetic Algorithm has ended. ')
            for i in ret_weight:
                print i
                print ('RORAC : %f' % obj_func_ga_initial(i))
                print('xTVaR : '),
                print Ityt.Uwg(ITMC.MCbase(Premium_list, i, cycle), ITMC.MCbase(Loss_list, i, cycle),
                               ITMC.MCbase(Expense_list, i, cycle)).xtvar(alpha)
            pickle_write(ret_weight, global_opt_result + 'evolved_result.pkl')

        elif selector2 == '3':
            """
            Particle Swarm Optimization tentative ver Oct15
            """
            print('-' * 100)
            print('Global Optimization by PSO')
            stime = time.time()

            p = Pool(7)
            opt_prob_iter = [opt_prob] * alpso_cycle
            alpso_ret_list = p.map(alpso_wrapper, opt_prob_iter)

            optimized_list = []
            optimized_weight = []
            for i in alpso_ret_list:
                optimized_list.append(i[0] * -1.)
                optimized_weight.append(list(i[1]))
                print i
            indexer = np.array(optimized_list).argsort()

            top_five = []
            if alpso_cycle >= 5:
                for i in range(5):
                    j = indexer[alpso_cycle - i - 1]
                    top_five.append(list(np.array(optimized_weight[j]) * np.array(alpso_weight) + 1.))
                pickle_write(top_five, global_opt_result + 'alpso_result.pkl')
            else:
                for i in range(alpso_cycle):
                    j = indexer[alpso_cycle - i - 1]
                    top_five.append(list(np.array(optimized_weight[j]) * np.array(alpso_weight) + 1.))
                pickle_write(top_five, global_opt_result + 'alpso_result.pkl')

            p.close()
            etime = time.time()
            print ('elapsed time : %f' % (etime - stime))

            fig, ax = plt.subplots(1, 1)
            ax.plot(np.arange(alpso_cycle) + 1, optimized_list, '.', ms=8, color='crimson')
            ax.set_xlabel('iteration')
            plt.tight_layout()
            plt.show()

        elif selector2 == '4':
            """
            Harmonic Search Algorithm tentative ver Oct15
            """
            print('-' * 100)
            print('Global Optimization by ALHSO')
            alpso_ret_list = []
            alhso = ALHSO()
            alhso.setOption('hms', 30)
            stime = time.time()
            for i in range(alhso_n):
                temp = alhso(opt_prob)
                alpso_ret_list.append(temp[0])
                print opt_prob.solution(0)
                opt_prob.delSol(0)
                print('%d th iteration' % i)
            etime = time.time()
            print ('elapsed time : %f' % (etime - stime))
            fig, ax = plt.subplots(1, 1)
            ax.hist(alpso_ret_list, alhso_n, color='azure')
            ax.set_xlabel('function value')
            plt.tight_layout()


        else:
            pass

        print('Global Optimization has finised. \n')
    elif selector1 == '2':

        """
        SLSQP main routine
        """

        print('*' * 100)
        print(' Local Optimization ')
        print('Select initial points :')
        print('(1) : Monte Carlo results \n (2) : Genetic Algorithm results \n (3) : ALPSO Algorithm results')
        print('Input 1 or 2 or 3 : '),
        selector3 = raw_input()

        plt.ion()  # Ready for graph drawing
        fig, axes = plt.subplots(2, 1)

        if selector3 == '1':
            nearest_element_temp = pickle_read(global_opt_result + 'clustered_result.pkl')
        elif selector3 == '2':
            nearest_element_temp = pickle_read(global_opt_result + 'evolved_result.pkl')
        else:
            nearest_element_temp = pickle_read(global_opt_result + 'alpso_result.pkl')

        # i_SLSQP = 1  # iteration variable
        final_result = []
        t1 = time.time()

        for ii in range(len(nearest_element_temp)):
            x0 = np.array(nearest_element_temp[ii])
            local_result = minimize(obj_func, x0, bounds=bnds.T, method="SLSQP", constraints=local_const,
                                    callback=callback_func,
                                    options={'disp': True, 'ftol': 1e-6, 'maxiter': 100})
            print local_result
            print('-' * 100 + '\n')
            final_result.append(local_result)

        t2 = time.time()

        print ('-' * 100)
        print('elapsed time : %d (s) (%f (m))' % ((t2 - t1), ((t2 - t1) / 60)))

        final_result_average = []
        ret_weight = []
        for i in range(len(final_result)):
            final_result_average.append(final_result[i].fun)
            ret_weight.append(final_result[i].x)
        pickle_write(final_result, local_opt_result + 'final_result_incAllDATA.pkl')
        result_array = [weight_list]
        for i in final_result:
            result_list = list(i.x)
            result_list.append(i.fun)
            result_array.append(result_list)
        result_df = pd.DataFrame(result_array)
        result_df.to_csv(local_opt_result + 'final_result_incAllDATA.csv')

        ret_weight = np.average(ret_weight, axis=0)
        ret_weight = list(ret_weight)
        pickle_write(ret_weight, local_opt_result + 'opt_w.pkl')
        print('Local Optimization has finised ! ')

        axes[1].clear()
        axes[1].grid(True)
        axes[1].set_xticks(range(len(weight_list)))
        if len(weight_list) < 11:
            axes[1].set_xticklabels(weight_list, fontsize=8)
        else:
            pass
        axes[1].set_ylabel('Biz shares')
        axes[1].set_ylim(0, 1.25)
        axes[1].bar(range(len(ret_weight)), ret_weight, align='center')
        plt.tight_layout()
        plt.show(block=True)

        # print('Result summary \n')
        # print('default xTVaR : %f \n' % xTVaR(w0))
        # print('default RORAC : %f \n' % RORAC(w0))
        # print('xTVaR : %f \n' % xTVaR(opt_w))
        # print('RORAC : %f \n' % RORAC(opt_w))
    else:
        print('bye')
