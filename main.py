import numpy as np
import pandas as pd
import models
import viz
import input

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# data pruning
n_zones = 263
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()
df = df.reindex(pd.MultiIndex.from_product([zones, zones], names=df.index.names), fill_value=0)

# SYSTEM VIEW
# add boroughs to dataframe and add binary value if a bridge is used on a trip
df['borough_origin'] = df.apply(lambda x: gdf.loc[x.name[0],'borough'], axis=1)
df['borough_dest'] = df.apply(lambda x: gdf.loc[x.name[1],'borough'], axis=1)
df['bridge_used'] = df.apply(lambda x:
                             (not (x['borough_origin']==x['borough_dest'] or
                              (x['borough_origin']=='Queens' and x['borough_dest']=='Brooklyn') or
                              (x['borough_origin']=='Brooklyn' and x['borough_dest']=='Queens')
                              )), axis=1)
pd.set_option('display.max_columns', None)
# set all non-bridge connection to highest air travel time to avoid using them (system view)
df.loc[df['bridge_used'] == False, 'air_travel_time'] = df['ground_travel_time'].max()
# ALTERNATIVE
# delete non bridge connections from dataframe
#df = df.loc[df.bridge_used, :]
#print(df[df['borough_origin']=='Queens'])

# call model
hubs, obj = models.model_a_ga(df, 8)
# df, hubs, obj = models.model_a(df, 5)

viz.viz_hubs(df, gdf, hubs)

# calculate total system relief
beta = 1
g = ((df['ground_travel_time'] / pd.to_timedelta(1, 'h')).to_numpy()*beta)
d = df['n_trips'].to_numpy()
sys_relief = (g*d).sum()
print("Total System Relief: " + str(sys_relief - obj))
