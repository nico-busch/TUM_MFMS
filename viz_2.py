import numpy as np
import pandas as pd
import models
import viz
import input
import sys

df = pd.read_pickle('results/df.pkl')

# create df_hubs for counting all trips going through a hub connection
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