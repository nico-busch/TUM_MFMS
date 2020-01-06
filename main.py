import pandas as pd
import models
import viz

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# data pruning
n_zones = 25
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()

df, hubs, obj = models.model_a(df, 5, alpha=5/60, beta=1)
if hubs.size > 0:
    viz.viz_hubs(df, gdf, hubs)
