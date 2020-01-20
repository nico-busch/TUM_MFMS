import numpy as np
import pandas as pd

import models
import study
import plots
import viz
import input

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# df = pd.read_pickle('data/trips_chicago.pkl')
# gdf = pd.read_pickle('data/zones_chicago.pkl')

# study.sensitivity_analysis(df_).to_pickle('results/results.pkl')
# study.gurobi_vs_ga(df).to_pickle('results/gurobi_vs_ga.pkl')

results = pd.read_pickle('results/results.pkl')

plots.plot_travel_time(results)
plots.plot_obj(results)

# obj, hubs, trips = models.model_a_ga(df, 5)
# viz.viz_hubs(df, gdf, hubs)

