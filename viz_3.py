import numpy as np
import pandas as pd
import models
import matplotlib.pyplot as plt
import seaborn as sns


'''
    Heatmap showing the demand (number of trips) from one hub to another aggregated from both directions
'''

# data preperation
n_zones = 50
n_hubs = 5
data = pd.read_pickle('data/trips_ny.pkl')
total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
        (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
zones = total.nlargest(n_zones).index.sort_values()
data_ = data.loc[(zones, zones), :]
data_.index = data_.index.remove_unused_levels()
data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

h_ = [10]
#h_ = [4, 5, 6, 7, 8, 9, 10]
count_ = 0
fig, axs = plt.subplots(1, 1)

for k in range(1):
    for l in range(1):

        # run Genetic Algorithm
        _, _, df = models.model_a_ga(data_, h_[count_])
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

        # plot heatmap
        df_ = df_hubs.copy()
        # round values
        df_['trip_count'] = (df_['trip_count'] / 1000).astype(int)
        df_ = df_.reset_index().pivot(columns='destination',index='origin',values='trip_count')
        df_ = df_.fillna(0)
        df_ = df_.astype(int)
        #axs[k, l] = sns.heatmap(df_, cmap="YlGnBu", fmt='', square=True, linewidths=1,
        #                        cbar_kws={'label': 'Number of trips [k]'}, ax=axs[k,l])

        sns.heatmap(df_, cmap="YlGnBu", annot=True, fmt='', square=True, linewidths=1,
                    cbar_kws={'label': 'Number of trips [k]'})
        #axs[k, l].set_title('Number of hubs: ' + str(h_[count_-1]))

        ''' Alternative with only half of Matrix displayed
        mask = np.zeros_like(df_)
        mask[np.triu_indices_from(mask)] = True
        df_ = df_.fillna(0)
        df_ = df_.astype(int)
        with sns.axes_style("white"):
            ax = sns.heatmap(df_, mask=mask, cmap="YlGnBu", annot=True, fmt='', square=True)
    '''

#plt.title('Number of trips for each hub connection')
plt.show()