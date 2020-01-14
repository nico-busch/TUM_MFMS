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
pred = np.load('pred_matrix.npy')
d = np.load('d_matrix.npy')
hubs = np.load('hubs_tmp.npy')
tmp = np.load('tmp.npy')

print(hubs)

def createPaths(p, i, j, first=False):
    if(p[i,j] == -9999):
        return np.NAN
    elif(p[i,j]==i):
        return (zones[i], zones[j])
    else:
        return createPaths(p, i, p[i, j]) + (zones[j],)

'''
def path(p, i, j):
    tuple_ = tuple(createPaths(p, i, j, True))
    if(not tuple_ or tuple_==None or tuple_==np.NaN):
        return np.NaN
    tuple_ = [x for x in tuple_ if x in hubs]
    print('tuple: ' + str(tuple_))
    return tuple_
'''

paths = pd.Series({(zones[i], zones[j]): createPaths(pred, i, j) for i in range(zones.size) for j in range(zones.size)},
                  name='paths')

np.set_printoptions(threshold=sys.maxsize)
print(paths)



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