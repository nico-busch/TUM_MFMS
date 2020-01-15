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
n_zones = 10
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()
idx = df.index.get_level_values(0).unique().union(df.index.get_level_values(0).unique())
df = df.reindex(pd.MultiIndex.from_product([zones, zones], names=df.index.names), fill_value=0)

results = study.sensitivity_analysis(df)
results.to_pickle('results/results.pkl')

results = pd.read_pickle('results/results.pkl')
plots.plot_travel_time(results)
exit()

# call model
# hubs, obj, pred, tmp = models.model_a_ga(df, 5)
df, hubs, obj = models.model_a(df, 5)
exit()
# results = study.sensitivity_analysis(df)
# results.to_pickle('results/results.pkl')
# results = pd.read_pickle('results/results.pkl')
# plots.plot_obj(results)

np.save('pred_matrix', pred)
np.save('hubs_tmp', hubs)
np.save('tmp', tmp)

viz.viz_hubs(df, gdf, hubs)

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
