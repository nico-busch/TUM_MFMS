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

    for i, ((alpha, beta), x) in enumerate(results.groupby(['alpha', 'beta'])):
        ax = axes.flatten()[i]
        ax.bar(x.index.get_level_values('p'), x['air_travel_time'], color='tab:green', edgecolor='white')
        ax.bar(x.index.get_level_values('p'), x['ground_travel_time'], bottom=x['air_travel_time'],
               color='tab:blue', edgecolor='white')

    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    plt.grid(False)
    plt.xlabel('number of hubs')
    plt.ylabel('objective value')
    plt.show()
