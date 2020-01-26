import pandas as pd
from matplotlib import ticker
import matplotlib.pyplot as plt


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
