import numpy as np
import pandas as pd
import models
import viz

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# data pruning
n_zones = 10
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()
df = df.reindex(pd.MultiIndex.from_product([zones, zones]), fill_value=0)

df1, hubs1, obj1 = models.model_a(df, 5, 0, beta=1)
df2, hubs2, obj2 = models.model_b(df, 5, 0, beta=1)

print(hubs1, obj1)
print(hubs2, obj2)

# if hubs.size > 0:
#     viz.viz_hubs(df, gdf, hubs)
