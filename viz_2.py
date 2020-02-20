import numpy as np
import pandas as pd
import models
#import viz
import input
import sys
import seaborn as sns
import matplotlib.pyplot as plt # due to release problems older version is needed -> downgrade to 3.1.0

'''
    Heatmap showing the demand (number of trips) from one hub to another
'''

# data preperation
data = pd.read_pickle('data/trips_ny.pkl')
total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
        (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
n_zones = 263
zones = total.nlargest(n_zones).index.sort_values()
data_ = data.loc[(zones, zones), :]
data_.index = data_.index.remove_unused_levels()
data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

# run Genetic Algorithm
_, _, df = models.model_a_ga(data_, 3, alpha=5/60, beta=1)

# create df_hubs for counting all trips going through a hub connection
un = df['hubs'].unique()
un = np.delete(un,0) # delete nan value
df_hubs = pd.DataFrame(data=un.flatten(), columns=['hubs'])
df_hubs = df_hubs.set_index('hubs')
df_hubs['trip_count'] = 0
for index, row in df_hubs.iterrows():
    df_hubs.loc[index,'trip_count'] = df.loc[df['hubs'] == tuple(index)]['n_trips'].sum()
df_hubs.index = pd.MultiIndex.from_tuples(df_hubs.index, names=('origin', 'destination'))
df_hubs.index = df_hubs.index.drop_duplicates(keep='first')

# plot heatmap
df_ = df_hubs.copy()
df_['trip_count'] = (df_['trip_count'] / 1000).astype(int) # round values
df_ = df_.reset_index().pivot(columns='destination',index='origin',values='trip_count')
df_ = df_.fillna(0)
df_ = df_.astype(int)
sns.heatmap(df_, cmap="YlGnBu", annot=True, fmt='', square=True, linewidths=1,
            cbar_kws={'label': 'Number of trips [k]'})
plt.show()