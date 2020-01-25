import pandas as pd
from itertools import product
import models
import timeit

def sensitivity_analysis(df):

    p = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    alpha = [0, 5/60, 10/60]
    beta = [1, 1.1]

    results = pd.DataFrame(columns=['p', 'alpha', 'beta', 'obj', 'air_travel_time', 'ground_travel_time', 'hubs'])
    results = results.set_index(['p', 'alpha', 'beta'])

    for p, alpha, beta in product(p, alpha, beta):
        obj, hubs, trips = models.model_a_ga(df, p, alpha=alpha, beta=beta)
        air_travel_time = (trips.loc[trips['hubs'].notna(), 'n_trips'] *
                           trips.loc[trips['hubs'].notna(), 'travel_time']).sum() / pd.to_timedelta(1, 'h')
        # n_trips = trips.groupby('hubs')['n_trips'].sum()
        # n_trips.index = pd.MultiIndex.from_tuples(n_trips.index, names=df.index.names)
        # air_travel_time = (n_trips * df[df.index.isin(n_trips.index)]['air_travel_time']).sum()
        ground_travel_time = obj - air_travel_time
        results.loc[p, alpha, beta] = obj, air_travel_time, ground_travel_time, hubs

    return results

def gurobi_vs_ga(df):

    n_zones = [60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260]
    p = [5]

    results = pd.DataFrame(columns=['method', 'n_zones', 'p', 'obj', 'runtime'])
    results = results.set_index(['method', 'n_zones', 'p'])

    total = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum() + \
            (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()

    for n_zones, p in product(n_zones, p):

        zones = total.nlargest(n_zones).index.sort_values()
        df_ = df.loc[(zones, zones), :]
        df_.index = df_.index.remove_unused_levels()

        # start_time = timeit.default_timer()
        # obj, _ = models.model_a(df_, p)
        # results.loc['Gurobi', n_zones, p] = obj, timeit.default_timer() - start_time

        start_time = timeit.default_timer()
        obj, _, _ = models.model_a_ga(df_, p)
        results.loc['GA', n_zones, p] = obj, timeit.default_timer() - start_time

    return results
