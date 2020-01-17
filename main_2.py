import numpy as np
import pandas as pd
import models
import viz
import input
import sys

df = pd.read_pickle('data/trips_ny.pkl')

# data pruning
n_zones = 263
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
df.index = df.index.remove_unused_levels()
df = df.reindex(pd.MultiIndex.from_product([zones, zones], names=df.index.names), fill_value=0)
zones = df.index.get_level_values(0).unique()
gdf = pd.read_pickle('data/zones_ny.pkl')

# import der zwischengespeicherten Files
#pred = np.load('results/pred_matrix.npy')
#hubs = np.load('results/hubs_tmp.npy')

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

# create df for counting all trips going through a hub connection
un = df['hubs'].unique()
un = np.delete(un,0) # delete nan value
df_hubs = pd.DataFrame(data=un.flatten(), columns=['hubs'])
df_hubs = df_hubs.set_index('hubs')
df_hubs['trip_count'] = 0
for index, row in df_hubs.iterrows():
    df_hubs.loc[index,'trip_count'] = df.loc[df['hubs'] == tuple(index)]['n_trips'].sum()

df_hubs.to_pickle('results/hub_connections.pkl')
df_hubs = pd.read_pickle('results/hub_connections.pkl')

print(df_hubs)


exit()

'''

_____________________________________________________________________________________________________

# SYSTEM VIEW
# INSERT IN MAIN IF REQUIRED
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
'''