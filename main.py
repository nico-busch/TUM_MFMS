import numpy as np
import pandas as pd
import models
import study
import plots
import viz
import input

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# # data pruning
n_zones = 263
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()
idx = df.index.get_level_values(0).unique().union(df.index.get_level_values(0).unique())
df = df.reindex(pd.MultiIndex.from_product([zones, zones], names=df.index.names), fill_value=0)

# results = study.sensitivity_analysis(df)
# results.to_pickle('results/results.pkl')

#results = pd.read_pickle('results/results.pkl')
#plots.plot_travel_time(results)
#exit()

# call model
hubs, obj, pred, tmp = models.model_a_ga(df, 5)
#df, hubs, obj = models.model_a(df, 5)

# results = study.sensitivity_analysis(df)
# results.to_pickle('results/results.pkl')
# results = pd.read_pickle('results/results.pkl')
# plots.plot_obj(results)

# ADD IN OLI
#____________________________________________________________________________________________________________

# Code for path reconstruction
def createPaths(p, i, j, first=False):
    if(p[i,j] == -9999):
        return (np.NAN,)
    elif(p[i,j]==i):
        return (zones[i], zones[j])
    else:
        return createPaths(p, i, p[i, j]) + (zones[j],)

# dictionary saving the reconstructed paths
paths = pd.Series({(zones[i], zones[j]): createPaths(pred, i, j) for i in range(zones.size) for j in range(zones.size)},
                  name='paths')
# only save the connecting hubs
for key, value in paths.items():
    value = np.array(value)
    tmp = value[np.isin(value, hubs)]
    if(len(tmp)> 1):
        paths[key] = tuple(tmp)
    else:
        paths[key] = np.NAN

# add hub information to the general dataframe
df["hubs"] = pd.Series(paths)

# save the general dataframe
df.to_pickle('results/df.pkl')

#____________________________________________________________________________________________________________

viz.viz_hubs(df, gdf, hubs)

exit()

# calculate total system relief
beta = 1
g = ((df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy()*beta)
d = df['n_trips'].to_numpy()
max_ = (g*d).sum()
print("Total System Relief: " + str(max_ - obj))
# hubs, obj = models.model_a_ga(df, 5, beta=1.1, alpha=5/60)
df, hubs, obj = models.model_a(df, 5, beta=1, alpha=0)
#
viz.viz_hubs(df, gdf, hubs)
#
# beta = 1
# g = ((df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy() * beta)
# d = df['n_trips'].to_numpy()
# sys_relief = (g * d).sum()
# print("Total System Relief: " + str((sys_relief - obj) / sys_relief))
