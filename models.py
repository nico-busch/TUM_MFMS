import numpy as np
import pandas as pd
from gurobipy import *

def model_a(df, p, alpha=0, beta=1):

    # parameter preparation
    routes = df.index
    zones = df.index.get_level_values(0).unique()
    n_zones = zones.size
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
    x = model.addVars(routes, routes, obj=x_coeff, vtype=GRB.BINARY)
    y = model.addVars(routes, obj=y_coeff, vtype=GRB.BINARY)
    z = model.addVars(zones, vtype=GRB.BINARY)
    model.modelSense = GRB.MINIMIZE

    # constraints
    model.addConstr(z.sum() <= p)
    model.addConstrs(x.sum(i, j, '*', '*') + y[i, j] == 1 for i, j in routes)
    # model.addConstrs(x[i, j, k, l] <= z[k] for i, j in routes for k, l in routes)
    # model.addConstrs(x[i, j, k, l] <= z[l] for i, j in routes for k, l in routes)
    model.addConstrs(x.sum('*', '*', k, '*') <= n_zones * (n_zones - p + 1) * z[k] for k in zones)
    model.addConstrs(x.sum('*', '*', '*', l) <= n_zones * (n_zones - p + 1) * z[l] for l in zones)

    # optimize
    model.optimize()

    # solution
    trips_air = pd.Series({(k1, k2): (k3, k4) for (k1, k2, k3, k4), v in x.items() if v.X == 1}, name='hubs')
    trips_air.index.names = df.index.names
    df = df.join(trips_air, how='left')
    hubs = np.array([k for k, v in z.items() if v.X == 1])
    obj = model.getObjective().getValue()

    return df, hubs, obj
