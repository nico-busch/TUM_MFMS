import numpy as np
import pandas as pd
from gurobipy import *

def model_a(df, p, alpha=0, beta=1):

    # parameter preparation
    routes = df.index
    zones = df.index.get_level_values(0).unique()
    shape = routes.levshape
    g = (df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape)
    a = (df['air_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape)
    d = df['n_trips'].to_numpy().reshape(shape)

    # coefficients
    x_coeff = (beta * (g[:, np.newaxis, :, np.newaxis] + g[:, np.newaxis, :]) + a + 2 * alpha) \
              * d[:, :, np.newaxis, np.newaxis]
    y_coeff = beta * g * d

    # model
    model = Model()
    model.setParam('TimeLimit', 1800)
    x = model.addVars(routes, routes, obj=x_coeff)
    y = model.addVars(routes, obj=y_coeff)
    z = model.addVars(zones, vtype=GRB.BINARY)
    model.modelSense = GRB.MINIMIZE

    # constraints
    model.addConstr(z.sum() <= p)
    model.addConstrs(x.sum(i, j, '*', '*') + y[i, j] == 1 for i, j in routes)
    model.addConstrs(x.sum(i, j, k, '*') <= z[k] for i, j in routes for k in zones)
    model.addConstrs(x.sum(i, j, '*', l) <= z[l] for i, j in routes for l in zones)

    # optimize
    model.optimize()

    # solution
    trips_air = pd.Series({(k1, k2): (k3, k4) for (k1, k2, k3, k4), v in x.items() if v.X == 1}, name='hubs')
    trips_air.index.names = df.index.names
    df = df.join(trips_air, how='left')
    hubs = np.array([k for k, v in z.items() if v.X == 1])
    obj = model.getObjective().getValue()

    return df, hubs, obj


def model_b(df, p, alpha=0, beta=1):

    # parameter preparation
    routes = df.index
    zones = df.index.get_level_values(0).unique()
    n_zones = zones.size
    shape = routes.levshape
    g = (df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape)
    a = (df['air_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy().reshape(shape)
    d = df['n_trips'].to_numpy().reshape(shape)

    # coefficients
    x_coeff = np.tile(g, (n_zones, 1, 1))
    y_coeff = np.tile(a, (n_zones, 1, 1))
    z_coeff = g
    w_coeff = g

    # model
    model = Model()
    model.setParam('TimeLimit', 1800)
    x = model.addVars(zones, routes, obj=x_coeff)
    y = model.addVars(zones, routes, obj=y_coeff)
    z = model.addVars(routes, obj=z_coeff)
    w = model.addVars(routes, obj=w_coeff)
    h = model.addVars(zones, vtype=GRB.BINARY)
    model.modelSense = GRB.MINIMIZE

    # constraints
    model.addConstr(h.sum() <= p)
    model.addConstrs(z.sum(i, '*') + w.sum(i, '*') == np.sum(d[zones.get_loc(i)]) for i in zones)
    model.addConstrs(x.sum(i, '*', j) + w[i, j] == d[zones.get_loc(i), zones.get_loc(j)] for i, j in routes)
    model.addConstrs(y.sum(i, k, '*') + x.sum(i, k, '*') - y.sum(i, '*', k) - z[i, k] == 0 for i, k in routes)
    model.addConstrs(z[i, k] <= np.sum(d[zones.get_loc(i)]) * h[k] for i, k in routes)
    model.addConstrs(x.sum('*', l, j) <= np.sum(d[:, zones.get_loc(j)]) * h[l] for l, j in routes)

    # optimize
    model.optimize()

    # solution
    hubs = np.array([k for k, v in h.items() if v.X == 1])
    obj = model.getObjective().getValue()

    return df, hubs, obj
