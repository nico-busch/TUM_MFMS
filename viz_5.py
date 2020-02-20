import numpy as np
import pandas as pd
import models
import viz
import input
import sys
import matplotlib.pyplot as plt
import seaborn as sns

'''
    Heatmap showing the demand (number of trips) from one hub to another aggregated from both directions
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

df_total = pd.DataFrame(columns=['trip_type', 'trip_count', 'p', 'percentage'])

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
        un = np.array(['direct', 'one_transfer', 'two_transfer'])
        df_ = pd.DataFrame(data=un.flatten(), columns=['trip_type'])
        df_['trip_count'] = np.NAN
        df_['p'] = i
        df_['percentage'] = df[df['trip_type'] != 'non_air']['n_trips'].sum()
        count = 0
        for i in un:
            df_.loc[count, 'trip_count'] = df[df['trip_type']==i]['n_trips'].sum()
            df_.loc[count, 'percentage'] = df_.loc[count, 'trip_count'] / df_.loc[count, 'percentage']
            count = count + 1
        df_total = df_total.append(df_, ignore_index=True)



colors = ["#006D2C", "#31A354","#74C476"]
pivot_df = df_total.pivot(index='p', columns='trip_type', values='percentage')
pivot_df.plot.bar(stacked=True, color=colors, figsize=(10,7))
plt.tight_layout()
plt.title('Proportion of each air trip type for different number of hubs')
plt.show()

df_total.to_pickle('results/df_total.pkl')

exit()



''' OLD CODE -> DO NOT DELETE YET

df_.plot.bar(rot=0, cmap="Set3")
#ax = plt.subplots()
#ax = df_.plot.pie(y='trip_count', cmap="Set3")
#ax.set_ylabel('')
plt.show()

exit()

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

print(df_hubs)
exit()


# aggregate both demand direction of a hub connection to one single value
tmp = df_hubs.copy()
existing_indexes = []
for index, row in df_hubs.iterrows():
    df_hubs.loc[index] = tmp.loc[index] + tmp.loc[(index[1], index[0])] + 0

# create dataframe representing the hub importance (number of trips)
df_ = pd.DataFrame(data=hubs.flatten(), columns=['hubs'])
df_['trip_count'] = 0
df_ = df_.set_index('hubs')
for i in hubs:
    for j in hubs:
        if(i != j):
            df_.loc[(i), 'trip_count'] = df_.loc[(i), 'trip_count'] + df_hubs.loc[(i, j), 'trip_count']

df_['trip_count'] = df_['trip_count'] / 1000
df_ = df_.sort_values(by=['trip_count'])
plt.show()
'''
