import pandas as pd
from itertools import product
import models

def sensitivity_analysis(df):

    p = [3, 4, 5, 6, 7, 8]
    alpha = [0, 1/60, 2/60]
    beta = [1, 1.01]

    results = pd.DataFrame(columns=['p', 'alpha', 'beta', 'obj', 'air_travel_time', 'ground_travel_time', 'hubs'])
    results = results.set_index(['p', 'alpha', 'beta'])

    for p, alpha, beta in product(p, alpha, beta):
        print(p, alpha, beta)
        obj, trips, hubs = models.model_a(df, p, alpha=alpha, beta=beta)
        air_travel_time = trips.loc[trips['hubs'].notna(), 'travel_time'].sum()
        ground_travel_time = trips.loc[trips['hubs'].isna(), 'travel_time'].sum()
        results.loc[p, alpha, beta, ] = obj, air_travel_time, ground_travel_time, hubs

    return results
