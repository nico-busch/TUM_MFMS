import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import floyd_warshall, reconstruct_path
from gurobipy import *
import timeit
# start = timeit.default_timer()
# print(timeit.default_timer() - start)
# import sys
# np.set_printoptions(threshold=sys.maxsize)

def model_a(df, p, alpha=0, beta=1):

    # parameter preparation
    routes = df.index
    zones = df.index.get_level_values(0).unique()
    shape = routes.levshape
    g = (df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) * beta
    a = (df['air_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) + 2 * alpha
    d = df['n_trips'].to_numpy().reshape(shape)

    # coefficients
    x_coeff = (g[:, np.newaxis, :, np.newaxis] + g[:, np.newaxis, :] + a) * d[:, :, np.newaxis, np.newaxis]
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
    trips = pd.Series({(k1, k2): (k3, k4) for (k1, k2, k3, k4), v in x.items() if v.X == 1}, name='hubs')
    trips.index.names = df.index.names
    df = df.join(trips, how='left')
    hubs = np.array([k for k, v in z.items() if v.X == 1])
    obj = model.getObjective().getValue()

    return df, hubs, obj

def model_a_ga(df, p, n_pop, n_cross, n_tour, p_mut, n_iter=100, alpha=0, beta=1):

    # parameter preparation
    zones = df.index.get_level_values(0).unique()
    shape = df.index.levshape
    n_zones = zones.size
    g = (df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) * beta
    a = (df['air_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape) + 2 * alpha
    d = df['n_trips'].to_numpy().reshape(shape)

    # initial solution
    # initial_hubs = np.argsort(np.sum(g * d, axis=0) + np.sum(g * d, axis=1))[::-1][:p]
    # pop = np.zeros([n_pop, n_zones], dtype=np.int64)
    # pop[:, initial_hubs] = 1

    pop = np.zeros([n_pop, n_zones], dtype=np.int64)
    initial_hubs = np.array([np.random.choice(n_zones, size=p, replace=False) for _ in range(n_pop)])
    pop[np.arange(n_pop)[:, np.newaxis], initial_hubs] = 1
    best_obj = np.inf
    best_z = None

    for x in range(n_iter):

        # fitness evaluation
        def fitness(z):
            non_hubs = (1 - z).astype(np.bool_)
            a_ = a.copy()
            a_[non_hubs, :], a_[:, non_hubs] = np.inf, np.inf
            obj = np.sum(floyd_warshall(csgraph=csr_matrix(np.minimum(g, a_))) * d)
            return obj
        pop_obj = np.apply_along_axis(fitness, 1, pop)

        if np.amin(pop_obj) < best_obj:
            idx = np.argmin(pop_obj)
            best_obj = pop_obj[idx]
            best_z = pop[idx]

        # selection
        par = pop[np.argmin(pop_obj[np.random.randint(n_pop, size=[n_pop, n_tour])], axis=1)]
        par1, par2 = np.split(par, 2)

        # crossover
        diff = par1 - par2
        where = (diff != 0).any(axis=1)
        idx1 = np.hstack([np.random.choice(np.where(diff[y] == 1)[0], 1) for y in range(diff.shape[0]) if where[y]])
        idx2 = np.hstack(([np.random.choice(np.where(diff[y] == -1)[0], 1) for y in range(diff.shape[0]) if where[y]]))
        off1, off2 = par1.copy(), par2.copy()
        off1[np.arange(off1.shape[0])[where], idx1], off2[np.arange(off2.shape[0])[where], idx1] = 0, 1
        off1[np.arange(off1.shape[0])[where], idx2], off2[np.arange(off2.shape[0])[where], idx2] = 1, 0
        off = np.vstack([off1, off2])

        # mutation
        k = n_zones - p
        idx1 = np.where(off == 0)[1].reshape(n_pop, k)[np.arange(n_pop), np.random.randint(k, size=n_pop)]
        idx2 = np.where(off == 1)[1].reshape(n_pop, p)[np.arange(n_pop), np.random.randint(p, size=n_pop)]
        mut = off.copy()
        mut[np.arange(n_pop), idx1], mut[np.arange(n_pop), idx2] = 1, 0
        mut = np.where(np.random.rand(n_pop)[:, np.newaxis] <= p_mut, mut, off)

        # new generation
        pop = mut

    return np.array(zones[best_z.astype(np.bool_)]), best_obj
