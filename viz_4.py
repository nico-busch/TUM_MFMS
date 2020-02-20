import numpy as np
import pandas as pd
import models
import viz
import input
import sys
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns


'''
    Hub importance 
'''

# data preperation
n_zones = 100
data = pd.read_pickle('data/trips_ny.pkl')
total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
        (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
zones = total.nlargest(n_zones).index.sort_values()
data_ = data.loc[(zones, zones), :]
data_.index = data_.index.remove_unused_levels()
data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

h_ = [2, 3, 4, 5, 6, 7]
count_ = 0
fig, axs = plt.subplots(2, 3)
for k in range(2):
    for l in range(3):

        # run Genetic Algorithm
        _, hubs, df = models.model_a_ga(data_, h_[count_])
        count_ = count_ + 1

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

        # aggregate both demand direction of a hub connection to one single value
        tmp = df_hubs.copy()
        existing_indexes = []
        for index, row in df_hubs.iterrows():
            df_hubs.loc[index] = tmp.loc[index] + tmp.loc[(index[1], index[0])] + 0

        # create dataframe representing the hub importance (number of trips)
        df_ = pd.DataFrame(data=hubs.flatten(), columns=['hubs'])
        df_['trip_count'] = 0
        df_['hubs_'] = df_['hubs']
        df_ = df_.set_index('hubs')
        for i in hubs:
            for j in hubs:
                if(i != j):
                    df_.loc[(i), 'trip_count'] = df_.loc[(i), 'trip_count'] + df_hubs.loc[(i, j), 'trip_count']

        df_['trip_count'] = df_['trip_count'] / 1000
        df_ = df_.sort_values(by=['trip_count'])

        # donut plot
        circle = plt.Circle( (0,0), 0.7, color='white')
        axs[k, l].pie(df_['trip_count'], labels=df_['hubs_'], wedgeprops = { 'linewidth' : 7, 'edgecolor' : 'white' })
        axs[k, l].add_artist(circle)
        axs[k, l].set_title('Number of hubs: ' + str(h_[count_-1]))

#plt.title('Number of trips at each hub')
plt.show()

# alternative plots
#df_.plot.pie(y='trip_count', cmap="Set3")
#df_.plot.bar(rot=0, cmap="Set3")