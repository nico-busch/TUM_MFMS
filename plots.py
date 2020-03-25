import pandas as pd
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np


def millions(x, pos):
    return '{:,.1f}M'.format(x / 10 ** 6)

def plot_travel_time(results):
    fig, axes = plt.subplots(nrows=results.index.get_level_values('beta').unique().size,
                             ncols=results.index.get_level_values('alpha').unique().size,
                             sharex=True, sharey=True)

    for i, ((beta, alpha), x) in enumerate(results.groupby(['beta', 'alpha'])):
        ax = axes.flatten()[i]
        ax.bar(x.index.get_level_values('p'), x['air_travel_time'].to_numpy(),
               color=(0/255, 82/255, 147/255), edgecolor='white', label='air travel time')
        ax.bar(x.index.get_level_values('p'), x['ground_travel_time'].to_numpy(), bottom=x['air_travel_time'].to_numpy(),
               color=(100/255, 160/255, 200/255), edgecolor='white', label='ground travel time')
        ax.text(0.02, 0.98, r'$\alpha = {:>0.0f}$min'.format(alpha * 60) + ', ' + r'$\beta = {:>0.1f}$'.format(beta),
                horizontalalignment='left', verticalalignment='top', transform=ax.transAxes)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(millions))
        handles, labels = ax.get_legend_handles_labels()
        plt.ylim(0, 10**7 + 2 * 10**6)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(prune='both'))

    ax = fig.add_subplot(111, frameon=False)
    ax.set_xticks([], [])
    ax.set_yticks([], [])
    ax.grid(False)
    plt.xlabel('number of hubs', labelpad=20)
    plt.ylabel('vehicle hours [h]', labelpad=45)
    plt.subplots_adjust(wspace=0, hspace=0)
    fig.legend(handles, labels, loc='upper center')
    plt.show()

def plot_gurobi_vs_ga(results):

    col = dict(zip(results.index.get_level_values('method').unique(),
                   [(227/255, 114/255, 34/255), (0/255, 82/255, 147/255)]))

    fig, ax = plt.subplots()

    for (method, p), x in results.groupby(['method', 'p']):
        ax.plot(x.index.get_level_values('n_zones'), x['runtime'], marker='o', color=col[method], label=method)

    ax.set_xlabel('number of zones')
    ax.set_ylabel('runtime [s]')
    ax.legend()
    plt.show()

def plot_time_savings_histogram(n_hubs=[3, 5, 7, 10], n_zones=263, alpha=5 / 60, beta=1):
    # data preperation
    data = pd.read_pickle('data/trips_ny.pkl')
    total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
            (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
    zones = total.nlargest(n_zones).index.sort_values()
    data_ = data.loc[(zones, zones), :]
    data_.index = data_.index.remove_unused_levels()
    data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

    '''
    # Only uncomment if new data calculation is wanted (~20min)

    for i in n_hubs:
        _, hubs, df = models.model_a_ga(data_, i, alpha=alpha, beta=beta)
        temp = (data_['ground_travel_time'] - df['travel_time']).loc[df['hubs'].notna()]
        temp[temp > pd.to_timedelta(3, 'h')] = pd.to_timedelta(0, 'h')
        temp[temp <= pd.to_timedelta(0, 'h')] = np.NaN
        temp = temp.dropna()
        savings = (temp / pd.to_timedelta(1, 'm')).rename('savings')
        savings.to_frame().to_pickle('results/histogram_data_'+str(i)+'_hubs.pkl')
    '''

    # histogram
    ncols = 2
    nrows = 2
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
    counter = 0
    title_c = 0
    for i in range(nrows):
        for j in range(ncols):
            ax = axes[i][j]
            df = pd.read_pickle('results/histogram_data_' + str(n_hubs[counter]) + '_hubs.pkl')
            # Plot when we have data
            if counter < 6:
                df = df.merge(data_['n_trips'], how='left', left_index=True, right_index=True)
                ax.hist(df['savings'], color='skyblue', alpha=0.8, label='{}'.format(n_hubs[counter]),
                        bins=range(0, 130, 2), weights=df.n_trips)
                ax.set_xlabel('Time savings [min]')
                ax.set_ylabel('Number of trips')
                ax.set_title('' + str(n_hubs[title_c]) + ' hubs')
                title_c = title_c + 1
                ax.set_ylim([0, 500000])
                ax.set_xlim([0, 60])
                start, end = ax.get_xlim()
                ax.xaxis.set_ticks(np.arange(0, end, 10))
            # Remove axis when we no longer have data
            else:
                ax.set_axis_off()
            counter += 1
    fig.tight_layout()
    plt.show()