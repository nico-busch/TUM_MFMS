import numpy as np
import pandas as pd
import models
import viz
import input

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# data pruning
n_zones = 10
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()
df = df.reindex(pd.MultiIndex.from_product([zones, zones], names=df.index.names), fill_value=0)

hubs_ga, obj_ga = models.model_a_ga(df, 5, 10, n_cross=100, p_mut=1, n_tour=5, alpha=0, beta=1)
df, hubs, obj = models.model_a(df, 5, alpha=0, beta=1)
print(obj_ga, obj)
print(hubs_ga, hubs)
exit()

if hubs.size > 0:
    viz.viz_hubs(df, gdf, hubs)
