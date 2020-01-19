import numpy as np
import pandas as pd
from scipy.sparse.csgraph import floyd_warshall
from gurobipy import *
import timeit

def model_a(df, p, alpha=0, beta=1):

    # parameter preparation
    routes = df.index
    zones = df.index.get_level_values(0).unique()
    shape = routes.levshape
    g = (df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) * beta
    a = (df['air_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) + 2 * alpha
    d = df['n_trips'].to_numpy().reshape(shape)

    # coefficients
    x_coeff = (g[:, np.newaxis, :, np.newaxis] + g.T[:, np.newaxis, :] + a) * d[:, :, np.newaxis, np.newaxis]
    y_coeff = g * d

    # model
    model = Model()
    model.setParam('TimeLimit', 1800)
    x = model.addVars(routes, routes, obj=x_coeff)
    y = model.addVars(routes, obj=y_coeff)
    z = model.addVars(zones, vtype=GRB.BINARY)
    model.modelSense = GRB.MINIMIZE

    # constraints
    model.addConstr(z.sum() == p)
    model.addConstrs(x.sum(i, j, '*', '*') + y[i, j] == 1 for i, j in routes)
    model.addConstrs(x.sum(i, j, k, '*') <= z[k] for i, j in routes for k in zones)
    model.addConstrs(x.sum(i, j, '*', l) <= z[l] for i, j in routes for l in zones)

    # optimize
    model.optimize()

    # solution
    hubs = np.array([k for k, v in z.items() if v.X == 1])
    best_obj = model.getObjective().getValue()

    return best_obj, hubs

def model_a_ga(df, p, alpha=0, beta=1, n_pop=150, n_cross=100, n_tour=5, n_gen=10 ** 3, n_rep=100, p_mut=0.5):

    start_time = timeit.default_timer()
    print('Beginning Genetic Algorithm')
    print('{:<10}{:>15}{:>10}'.format('Gen', 'Best Fitness', 'Time'))

    # parameter preparation
    zones = df.index.get_level_values(0).unique()
    shape = df.index.levshape
    n_zones = zones.size
    g = (df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) * beta
    a = (df['air_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) + 2 * alpha
    d = df['n_trips'].to_numpy().reshape(shape)

    # result arrays
    pop = np.zeros([n_pop, n_zones], dtype=np.int64)
    pop_obj = np.full(n_pop, np.inf)
    best_z = None
    best_obj = np.inf
    rep = 0

    # initial population
    hubs_random = np.vstack([np.random.choice(n_zones, size=p, replace=False) for _ in range(n_pop // 3 * 2)])
    idx = np.argsort(np.sum(g * d, axis=0) + np.sum(g * d, axis=1))[::-1][:np.maximum(n_zones // 10, p)]
    hubs_guess = np.vstack([np.random.choice(idx, size=p, replace=False) for _ in range(n_pop // 3)])
    pop[np.arange(n_pop // 3 * 2)[:, np.newaxis], hubs_random] = 1
    pop[np.arange(n_pop // 3 * 2, n_pop)[:, np.newaxis], hubs_guess] = 1

    for x in range(n_gen):

        # fitness evaluation
        def fitness(z):
            non_hubs = ~z.astype(np.bool_)
            a_hubs = a.copy()
            a_hubs[non_hubs, :], a_hubs[:, non_hubs] = np.inf, np.inf
            obj = np.sum(floyd_warshall(np.minimum(g, a_hubs)) * d)
            return obj
        inf = pop_obj == np.inf
        pop_obj[inf] = np.apply_along_axis(fitness, 1, pop[inf])

        if np.amin(pop_obj) < best_obj:
            idx = np.argmin(pop_obj)
            best_obj = pop_obj[idx]
            best_z = pop[idx]
            rep = 0
            print('{:<10}{:>15.4f}{:>9.0f}{}'.format(x, best_obj, timeit.default_timer() - start_time, 's'))
        else:
            rep += 1
            if rep >= n_rep:
                break

        # selection
        tour = np.random.randint(n_pop, size=[n_cross, n_tour])
        par = pop[tour[np.arange(n_cross), np.argmin(pop_obj[tour], axis=1)]]
        par1, par2 = np.split(par, 2)

        # crossover
        off1, off2 = par1.copy(), par2.copy()
        diff = off1 - off2
        uneq = np.where(np.any(diff != 0, axis=1))[0]
        if uneq.size > 0:
            idx1 = np.hstack([np.random.choice(np.where(diff[y] > 0)[0], 1) for y in uneq])
            idx2 = np.hstack([np.random.choice(np.where(diff[y] < 0)[0], 1) for y in uneq])
            off1[uneq, idx1], off2[uneq, idx1] = 0, 1
            off1[uneq, idx2], off2[uneq, idx2] = 1, 0
        off = np.vstack([off1, off2])

        # mutation
        mut = off.copy()
        k = n_zones - p
        idx1 = np.where(off == 0)[1].reshape(n_cross, k)[np.arange(n_cross), np.random.randint(k, size=n_cross)]
        idx2 = np.where(off == 1)[1].reshape(n_cross, p)[np.arange(n_cross), np.random.randint(p, size=n_cross)]
        mut[np.arange(n_cross), idx1], mut[np.arange(n_cross), idx2] = 1, 0
        mut = np.where(np.random.rand(n_cross)[:, np.newaxis] <= p_mut, mut, off)

        # new generation
        idx = np.argsort(pop_obj)[:n_pop - n_cross]
        pop = np.vstack([pop[idx], mut])
        pop_obj = np.hstack([pop_obj[idx], np.full(n_cross, np.inf)])

    print('Termination criterion reached')
    print('{}{}'.format('Best objective value is ', best_obj))
    print('{}{}'.format('Time is ', timeit.default_timer() - start_time))

    # results
    non_hubs_ = ~best_z.astype(np.bool_)
    a_hubs_ = a.copy()
    a_hubs_[non_hubs_, :], a_hubs_[:, non_hubs_] = np.inf, np.inf
    idx = a_hubs_ <= g
    dist, pred = floyd_warshall(np.minimum(g, a_hubs_), return_predecessors=True)
    hubs = np.array(zones[best_z.astype(np.bool_)])

    def get_hubs(i, j):
        if pred[i, j] == -9999:
            return np.NAN
        elif np.all(np.isin([zones[pred[i, j]], zones[j]], hubs)) and idx[pred[i, j], j]:
            return zones[pred[i, j]], zones[j]
        else:
            return get_hubs(i, pred[i, j])

    hubs_loc = pd.Series({(i, j): get_hubs(zones.get_loc(i), zones.get_loc(j))
                         for i in zones for j in zones}, name='hubs')
    travel_time = pd.to_timedelta(pd.Series(np.ravel(dist), index=df.index, name='travel_time'), 'h')
    trips = pd.concat([travel_time, hubs_loc, df['n_trips']], axis=1)

    return best_obj, hubs, trips
