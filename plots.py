from matplotlib import ticker
import matplotlib.pyplot as plt


def plot_obj(results):
    fig, ax = plt.subplots()

    col = dict(zip(results.index.get_level_values('alpha').unique(),
                   ['tab:red', 'tab:blue', 'tab:green', 'tab:orange']))
    linestyle = dict(zip(results.index.get_level_values('beta').unique(),
                         ['-', '--']))

    for (alpha, beta), x in results.groupby(['alpha', 'beta']):
        ax.plot(x.index.get_level_values('p'), x['obj'],
                color=col[alpha], marker='o', linestyle=linestyle[beta], label=(alpha, beta))

    ax.set_xlabel("number of hubs")
    ax.set_ylabel("objective value")
    ax.legend()
    plt.show()


def plot_travel_time(results):
    fig, axes = plt.subplots(nrows=results.index.get_level_values('beta').unique().size,
                             ncols=results.index.get_level_values('alpha').unique().size,
                             sharex=True, sharey=True)

    def thousands(x, pos):
        return '{:,.0f}k'.format(x / 10 ** 3)

    for i, ((beta, alpha), x) in enumerate(results.groupby(['beta', 'alpha'])):
        ax = axes.flatten()[i]
        ax.bar(x.index.get_level_values('p'), x['air_travel_time'],
               color=(0/255, 82/255, 147/255), edgecolor='white', label='air_travel_time')
        ax.bar(x.index.get_level_values('p'), x['ground_travel_time'], bottom=x['air_travel_time'],
               color=(227/255, 114/255, 34/255), edgecolor='white', label='ground_travel_time')
        ax.title.set_text(r'$\alpha = {:>0.2f}, \beta$ = {:>0.1f}'.format(alpha, beta))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(thousands))
        handles, labels = ax.get_legend_handles_labels()

    ax = fig.add_subplot(111, frameon=False)
    ax.set_xticks([], [])
    ax.set_yticks([], [])
    ax.grid(False)
    plt.xlabel('number of hubs', labelpad=30)
    plt.ylabel('objective value', labelpad=30)
    plt.subplots_adjust(wspace=0.05, hspace=0.15)
    fig.legend(handles, labels, loc='upper center')
    plt.show()
