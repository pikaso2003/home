#
#   Comments :          GA module
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

import random
import array
import numpy as np
import matplotlib.pyplot as plt
from math import exp
from functools import partial
from deap import base, creator, tools, algorithms


# calc_func of value of individual element
def ind_value_maker(weight):
    biz_lower_lim = weight[0]
    biz_upper_lim = weight[1]
    return biz_lower_lim + (biz_upper_lim - biz_lower_lim) * random.random()


# constructor of an individual
def init_ind(ind_class, weight_list):
    for i in range(1, len(weight_list)):
        ind_class.append(ind_value_maker(weight_list[i]))
    return ind_class


# constructor of population
def init_pop(n_pop, weight_list, toolbox):
    creator.create('FitnessMax', base.Fitness, weights=(1.,))
    creator.create('Individual', list, fitness=creator.FitnessMax)
    toolbox.register('attribute', ind_value_maker, list(weight_list[0]))
    toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.attribute, n=1)
    ret = []
    for i in range(n_pop):
        ret.append(init_ind(toolbox.individual(), weight_list))
    return ret


def mutOpt(individual, weight_list, indpb):
    size = len(individual)
    biz_lower_lim = weight_list[0]
    biz_upper_lim = weight_list[1]
    for i, xl, xu in zip(range(size), biz_lower_lim, biz_upper_lim):
        if indpb > random.random():
            individual[i] = xl + (xu - xl) * random.random()
    return individual,


# GA main routine
def ga_main(bnds, n_pop, obj_func_ga, obj_func_ga_initial, cxpb, indpb, mutpb, ngen):
    global fits_g
    toolbox = base.Toolbox()
    pop = init_pop(n_pop, bnds.T, toolbox)
    toolbox.register('select', tools.selTournament, tournsize=2)
    toolbox.register('mate', tools.cxTwoPoint)
    toolbox.register('mutate', mutOpt, weight_list=bnds, indpb=indpb)
    toolbox.register('evaluate', obj_func_ga_initial)

    plt.ion()
    fig, ax = plt.subplots(1, 1)
    fits = map(toolbox.evaluate, pop)
    fits_0 = tools.selBest(pop, 5)
    for i in fits_0:
        plt.plot(obj_func_ga_initial(i), 'ro', ms=4)
    plt.draw()

    for g in range(ngen):

        toolbox.register('evaluate', obj_func_ga, ngen_count=g + 1)  # change the evaluate for setting penalty

        """
        selecting next generation
        """
        offspring = toolbox.select(pop, len(pop))
        offspring = map(toolbox.clone, offspring)

        """
        crossover
        """
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb + 0.2 * (g + 0.) / ngen:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        """
        mutation
        """
        for mutant in offspring:
            if random.random() < mutpb * exp(-(g - (ngen / 2)) ** 2 / 2 / (ngen / 6) ** 2):
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fits = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fits):
            ind.fitness.values = fit

        pop[:] = offspring
        fits_g = tools.selBest(pop, 5)
        for i in fits_g:
            plt.plot(g + 1, obj_func_ga_initial(i), 'ro', ms=4)
        plt.grid(True)
        plt.title('GA optimization : 5 elites plotted ')
        plt.xlabel('Generation')
        plt.ylabel('non-constrained \n objective function')
        plt.draw()
        print('%d th generation evolved' % g),
        print(' : obj func = %f' % obj_func_ga_initial(fits_g[4]))

    return fits_g
