import numpy as np
import pandas as pd
import models
import viz
import input
import sys
import matplotlib.pyplot as plt
import seaborn as sns

'''
    Avergae number of trips per hub
'''

# data preperation
n_zones = 263
n_hubs = 10
data = pd.read_pickle('data/trips_ny.pkl')
total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
        (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
zones = total.nlargest(n_zones).index.sort_values()
data_ = data.loc[(zones, zones), :]
data_.index = data_.index.remove_unused_levels()
data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

df_total = pd.DataFrame(columns=['p', 'trips_per_hub'])

for i in range(n_hubs + 1):
    if(i>=2):

        # run Genetic Algorithm
        _, hubs, df = models.model_a_ga(data_, i, alpha=5/60, beta=1)

        # adding trip transfer types information to df
        df['trip_type'] = 'non_air'
        for index, row in df.dropna().iterrows():
            tmp = tuple(row['hubs'])
            if((tmp[0]==index[0] and tmp[1]==index[1]) or (tmp[0]==index[1] and tmp[1]==index[0])):
                df.loc[index, 'trip_type'] = 'direct'
            elif(tmp[0]==index[0] or tmp[1]==index[1] or tmp[1]==index[0] or tmp[0]==index[1]):
                df.loc[index, 'trip_type'] = 'one_transfer'
            else:
                df.loc[index, 'trip_type'] = 'two_transfer'

        tph = df[df['trip_type'] != 'non_air']['n_trips'].sum()/i
        df2 = pd.DataFrame([[i, tph]], columns=['p', 'trips_per_hub'])
        df_total = df_total.append(df2, ignore_index=True)

df_total = df_total.set_index('p')
df_total.plot(style='.-')
plt.title('Average number of trips per hub [k]')

plt.show()