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
