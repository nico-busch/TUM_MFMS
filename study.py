import pandas as pd
from itertools import product
import models

def sensitivity_analysis(df):

    p = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    alpha = [0, 5/60, 10/60, 15/60]
    beta = [1, 1.1]

    results = pd.DataFrame(columns=['p', 'alpha', 'beta', 'hubs', 'obj'])
    results = results.set_index(['p', 'alpha', 'beta'])

    for p, alpha, beta in product(p, alpha, beta):
        results.loc[p, alpha, beta] = models.model_a_ga(df, p, alpha=alpha, beta=beta)

    return results
