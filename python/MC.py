"""
   Comments :   MonteCarlo

   Arguments : weight,

   Return :

 ---------------------------------------------------------------------------------
   Date        Developer       Action


"""

import os
import numpy as np
from numpy import random
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import math
from pandas import DataFrame
from scipy.optimize import minimize
import sys
import pickle
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from InsuranceTools.YearTable import peril_allocation, perillist_to_perilclass, peril_accumulator
from InsuranceTools.DataConverter import pickle_write, pickle_read


#   [ w_1, w_2, ... , w_n ]*[ Peril_class_1, Peril_class_2, ... , Peril_class_n ] -> MCbase_class [cycle row * 1 col]
#   construct MCbase object from Peril class list by peril_allocation
#   peril_class_list : list of class Peril
#   w : list of allocation
#   cycle : realization number
#   return : MCbase object summed up to one Peril
class MCbase(object):
    def __init__(self, peril_class_list, w, cycle):
        self.yt = peril_allocation(peril_class_list, w, cycle).yt
        self.name = peril_allocation(peril_class_list, w, cycle).name
        self.temp = np.sort(self.yt, axis=0)  # sorted YearTable
        self.alpha = 0.99  # default = 0.99 (100yr)
        self.var_n = 0  # VaR number
        self.var_m = 0  # for number of trunTVaR
        self.indexer = 0  # event index of each peril's YLQT number after sorted

    def alpha_check(self, alpha):

        if alpha >= 1.:
            print('-' * 100 + '\n')
            print(' alpha >=1 \n alpha must be less than 1 \n')
            print('-' * 100 + '\n')
            exit(1)
        else:
            self.alpha = alpha

    def mean(self):
        return np.mean(self.yt, axis=0)

    def var(self, alpha):
        self.alpha_check(alpha)
        self.var_n = np.int(np.floor(self.yt.shape[0] * alpha))
        return self.temp[self.var_n]

    def xvar(self, alpha):
        return self.var(alpha) - self.mean()

    def tvar(self, alpha):
        self.alpha_check(alpha)
        self.var_n = np.int(np.floor(self.yt.shape[0] * alpha))
        return np.mean(self.temp[self.var_n:self.yt.shape[0]], axis=0)

    def xtvar(self, alpha):
        self.alpha_check(alpha)
        return self.tvar(alpha) - np.mean(self.yt, axis=0)

    def truntvar(self, alpha, beta):
        self.alpha_check(alpha)
        self.alpha_check(beta)
        self.var_n = np.int(np.floor(self.yt.shape[0] * alpha))
        self.var_m = np.int(np.floor(self.yt.shape[0] * beta))
        return np.mean(self.temp[self.var_n:self.var_m], axis=0)


def constraints(const, w):
    boolean = 1
    for i in const:
        boolean *= i(w)
    return boolean


def weight_gen(w_lower, w_upper):
    random.seed()
    ret = np.array(w_lower) + (np.array(w_upper) - np.array(w_lower)) * random.random(
        len(w_lower))
    return list(ret)


# arg : x, y -> list
def clustering(x, y, num_clusters, result_w, global_opt_result):
    cluster_input = zip(scale(np.array(x)), scale(np.array(y)))
    cluster_input = np.array(cluster_input)
    km = KMeans(n_clusters=num_clusters, init='k-means++', verbose=1)
    km.fit(cluster_input)
    cluster_center = km.cluster_centers_

    nearest_number = []  # Element number close to clusterC[0,1,2,3,4, ...]

    for i in range(num_clusters):
        res_temp = float('inf')
        nearest = 0
        for j in range(len(x)):
            res = np.dot((cluster_input[j] - cluster_center[i]), (cluster_input[j] - cluster_center[i]).T)
            if res < res_temp:
                nearest = j
                res_temp = res
        nearest_number.append(nearest)

    ret_weight = []
    for i in nearest_number:
        ret_weight.append(result_w[i])
    pickle_write(ret_weight, global_opt_result + 'clustered_result.pkl')
    return km.labels_
