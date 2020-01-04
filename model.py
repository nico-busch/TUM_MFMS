import pandas as pd
import numpy as np
from gurobipy import *

# data preparation and pruning
n_zones = 25
df = pd.read_pickle('input.pkl')
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['PULocationID']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['DOLocationID']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
routes = df.index
shape = routes.remove_unused_levels().levshape

# params
g = df['ground_travel_time'].dt.total_seconds().to_numpy().reshape(shape)
a = df['air_travel_time'].dt.total_seconds().to_numpy().reshape(shape)
d = df['n_trips'].to_numpy().reshape(shape)
p = 5

# coefficients
x_coeff = g[:, np.newaxis, :, np.newaxis] + a + g[:, np.newaxis, :] * d[:, :, np.newaxis, np.newaxis]
y_coeff = g * d

# model
model = Model()
x = model.addVars(routes, routes, obj=x_coeff, vtype=GRB.BINARY)
y = model.addVars(routes, obj=y_coeff, vtype=GRB.BINARY)
z = model.addVars(zones, vtype=GRB.BINARY)
model.modelSense = GRB.MINIMIZE

# constraints
model.addConstr(z.sum() <= p)
model.addConstrs(x.sum(i, j, '*', '*') + y[i, j] == 1 for i, j in routes)
model.addConstrs(x[i, j, k, l] <= z[k] for i, j in routes for k, l in routes)
model.addConstrs(x[i, j, k, l] <= z[l] for i, j in routes for k, l in routes)
model.optimize()

# solution
hubs = zones[np.array([v.X for v in z.values()], dtype=bool)]
np.savetxt('hubs.csv', hubs, fmt='%i')
