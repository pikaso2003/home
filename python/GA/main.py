"""

How to implement GA algorithm               coded by hirayu 11.Sep.2015

1st step :  SCOPE creator
            Make creator class for individual having attribute for objective function

2nd step :  SCOPE toolbox(instance of Toolbox)
            Making the class initializing Individual and population

3rd step :  SCOPE toolbox
            Making evolution process

4th step :
            Main function


"""
import array
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from deap import base, creator, tools

# 1st step
# making creator class
creator.create('FitnessMax', base.Fitness, weights=(1.0,))
creator.create('Individual', list, fitness=creator.FitnessMax)

# 2nd step
# making class initializing individual and population under the scope of toolbox
# Note : scope
#       creator -> Individual
#       toolbox -> individual, population
IND_SIZE = 25

toolbox = base.Toolbox()
toolbox.register('attribute', random.randint, 0, 1)
toolbox.register('individual', tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
toolbox.register('population', tools.initRepeat, list, toolbox.individual)


# 3rd step
# making objective function
# Attention : return value
def evaluate(individual):
    return sum(individual),


toolbox.register('mate', tools.cxTwoPoint)
toolbox.register('mutate', tools.mutFlipBit, indpb=0.5)
toolbox.register('select', tools.selTournament, tournsize=3)
toolbox.register('evaluate', evaluate)


# 4th step
# main function
def main():
    pop = toolbox.population(n=100)  # constructing population,  pop number -> n
    cxpb, mutpb, ngen = 0.5, 0.2, 30  # probability of crossover, mutation   and   number of iteration cycle

    fitnesses = map(toolbox.evaluate, pop)  # evaluating all individuals in population
    for ind, fit in zip(pop, fitnesses):
        print(fit)
        ind.fitness.values = fit

    # select, crossover and mutation process
    for g in range(ngen):
        """
        selecting next generation
        """
        offspring = toolbox.select(pop, len(pop))
        offspring = map(toolbox.clone, offspring)

        """
        selecting offspring[0],[2],[4],[6]...as child1, selecting offspring[1],[3],[5],[7]... as child2
        for crossover
        """
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        """
        mutation
        """
        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

        fits = [ind.fitness.values[0] for ind in pop]
        best_ind = tools.selBest(pop, 1)[0]
        axes[0].plot(g, np.sum(best_ind), 'ro', ms=4)
        axes[1].plot(g, np.mean(fits), 'ko', ms=2)
        axes[2].plot(g, np.std(fits), 'go', ms=2)
        plt.draw()

        print('mean : %f' % np.mean(fits))
        print('std : %f' % np.std(fits))
        print('-' * 100)
        print('%d th generation is ...' % g)
        print(pop)

    return pop


print('-' * 100)
print('sim has started !')
print('-' * 100)
plt.ion()
fig, axes = plt.subplots(3, 1)
axes[0].set_xlabel('Simulation cycle')
axes[0].set_ylabel('Evaluation value \n Max=25')
axes[1].set_ylabel('mean of population')
axes[2].set_ylabel('std of population')
plt.tight_layout()
time1 = time.time()
pop = main()
time2 = time.time()
plt.show(block=True)
fits = [ind.fitness.values[0] for ind in pop]
print('mean : %f' % np.mean(fits))
print('std : %f' % np.std(fits))
print('*' * 100)
print('elapsed time : %d s' % int(time2 - time1))
best_ind = tools.selBest(pop, 1)[0]
print('Best individual is ...')
print(best_ind)
print('-'*100)
print('sim has finished .')
