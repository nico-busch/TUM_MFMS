import numpy as np
import pandas as pd
import models
import viz
import input
import sys
import matplotlib.pyplot as plt
import seaborn as sns

# data preperation
n_zones = 50
n_hubs = 7
data = pd.read_pickle('data/trips_ny.pkl')
total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
        (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
zones = total.nlargest(n_zones).index.sort_values()
data_ = data.loc[(zones, zones), :]
data_.index = data_.index.remove_unused_levels()
data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

w = 7
h = 7

fig = plt.figure(figsize=(w,5))


# run Genetic Algorithm
_, hubs, df = models.model_a_ga(data_, n_hubs)

# create df_hubs for counting all trips going through a hub connection
un = df['hubs'].unique()
un = np.delete(un, 0)  # delete nan value
un = np.sort(un)
df_hubs = pd.DataFrame(data=un.flatten(), columns=['hubs'])
df_hubs = df_hubs.set_index('hubs')
df_hubs['trip_count'] = 0
for index, row in df_hubs.iterrows():
    df_hubs.loc[index, 'trip_count'] = df.loc[df['hubs'] == tuple(index)]['n_trips'].sum()
df_hubs.index = pd.MultiIndex.from_tuples(df_hubs.index, names=('origin', 'destination'))
df_hubs.index = df_hubs.index.drop_duplicates(keep='first')

# aggregate both demand direction of a hub connection to one single value
tmp = df_hubs.copy()
existing_indexes = []
for index, row in df_hubs.iterrows():
    df_hubs.loc[index] = tmp.loc[index] + tmp.loc[(index[1], index[0])] + 0

# create dataframe representing the hub importance (number of trips)
hubs = np.sort(hubs)
df_imp = pd.DataFrame(data=hubs.flatten(), columns=['hubs'])
df_imp['trip_count'] = 0
df_imp['hubs_'] = df_imp['hubs']
df_imp = df_imp.set_index('hubs')
for i in hubs:
    for j in hubs:
        if (i != j):
            df_imp.loc[(i), 'trip_count'] = df_imp.loc[(i), 'trip_count'] + (df_hubs.loc[(i, j), 'trip_count']/ 1000).astype(int)

#df_imp['trip_count'] = df_imp['trip_count'] / 1000
#df_imp = df_imp.sort_values(by=['trip_count'])

# plot heatmap
df_ = df_hubs.copy()
# round values
df_['trip_count'] = (df_['trip_count'] / 1000).astype(int)
df_ = df_.reset_index().pivot(columns='destination', index='origin', values='trip_count')
df_ = df_.fillna(0)
df_ = df_.astype(int)

ax1 = plt.subplot2grid((w,h), (0,0), colspan=w-1, rowspan=h-1)
#ax2 = plt.subplot2grid((w,h), (w-1,0), colspan=w-1, rowspan=1)
ax3 = plt.subplot2grid((w,h), (0,h-1), colspan=1, rowspan=h-1)

mask = np.zeros_like(df_)
mask[np.tril_indices_from(mask)] = True

sns.heatmap(df_, ax=ax1, annot=True, cmap="YlGnBu",mask=mask, linecolor='w', cbar = False, fmt='', linewidths=1,
            cbar_kws={'label': 'Number of trips [k]'})
#ax1.xaxis.tick_top()
ax1.set_xticklabels(df_.columns, rotation=40)

#sns.heatmap((pd.DataFrame(df_.sum(axis=0))).transpose(), ax=ax2,  annot=True, cmap="YlGnBu", cbar=False, xticklabels=False, yticklabels=False)
#sns.heatmap(df_imp['trip_count'], ax=ax3,  annot=True, cmap="YlGnBu", cbar=False, xticklabels=False,
#            yticklabels=False, fmt='', linewidths=1, cbar_kws={'label': 'Number of trips [k]'})

#ax3 = sns.barplot(x=df_imp['trip_count'], y=df_imp['hubs_'].astype(str), color='b', orient = 'h')
#ax3.set_xlabel('trip_count'),

plt.show()

exit()
#----------------------------------------------------------------------------------------------------------

# run Genetic Algorithm
_, _, df = models.model_a_ga(data_, h_[count_])
count_ = count_ + 1

# create df_hubs for counting all trips going through a hub connection
un = df['hubs'].unique()
un = np.delete(un, 0)  # delete nan value
df_hubs = pd.DataFrame(data=un.flatten(), columns=['hubs'])
df_hubs = df_hubs.set_index('hubs')
df_hubs['trip_count'] = 0
for index, row in df_hubs.iterrows():
    df_hubs.loc[index, 'trip_count'] = df.loc[df['hubs'] == tuple(index)]['n_trips'].sum()
df_hubs.index = pd.MultiIndex.from_tuples(df_hubs.index, names=('origin', 'destination'))
df_hubs.index = df_hubs.index.drop_duplicates(keep='first')

# aggregate both demand direction of a hub connection to one single value
tmp = df_hubs.copy()
existing_indexes = []
for index, row in df_hubs.iterrows():
    df_hubs.loc[index] = tmp.loc[index] + tmp.loc[(index[1], index[0])] + 0

# plot heatmap
df_ = df_hubs.copy()
# round values
df_['trip_count'] = (df_['trip_count'] / 1000).astype(int)
df_ = df_.reset_index().pivot(columns='destination', index='origin', values='trip_count')
df_ = df_.fillna(0)
df_ = df_.astype(int)
# axs[k, l] = sns.heatmap(df_, cmap="YlGnBu", fmt='', square=True, linewidths=1,
#                        cbar_kws={'label': 'Number of trips [k]'}, ax=axs[k,l])

sns.heatmap(df_, cmap="YlGnBu", annot=True, fmt='', square=True, linewidths=1,
            cbar_kws={'label': 'Number of trips [k]'})
# axs[k, l].set_title('Number of hubs: ' + str(h_[count_-1]))