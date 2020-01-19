import numpy as np
import pandas as pd
import models
import viz
import input
import sys

data = pd.read_pickle('data/trips_ny.pkl')

total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
        (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()

n_zones = 50
zones = total.nlargest(n_zones).index.sort_values()
data_ = data.loc[(zones, zones), :]
data_.index = data_.index.remove_unused_levels()
data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

_, _, df = models.model_a_ga(data_, 5)

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