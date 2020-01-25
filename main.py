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

# study.sensitivity_analysis(df).to_pickle('results/sensitivity_analysis.pkl')
# study.gurobi_vs_ga(df).to_pickle('results/gurobi_vs_ga.pkl')

results = pd.read_pickle('results/gurobi_vs_ga.pkl')

plots.plot_gurobi_vs_ga(results)
exit()
# plots.plot_obj(results)
#
obj, hubs, trips = models.model_a_ga(df, 10)
viz.viz_hubs(df, gdf, hubs)

