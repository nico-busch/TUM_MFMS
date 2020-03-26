import numpy as np
import pandas as pd

import models
import study
import plots
import viz
import input

# df, gdf = input.input_ny()
# df, gdf = input.input_chicago()

df = pd.read_pickle('data/trips_ny.pkl')
gdf = pd.read_pickle('data/zones_ny.pkl')

# df = pd.read_pickle('data/trips_chicago.pkl')
# gdf = pd.read_pickle('data/zones_chicago.pkl')

viz.viz_zones(df, gdf)

study.sensitivity_analysis(df).to_pickle('results/sensitivity_analysis.pkl')
study.gurobi_vs_ga(df).to_pickle('results/gurobi_vs_ga.pkl')

results_sensitivity = pd.read_pickle('results/sensitivity_analysis.pkl')
results_gurobi = pd.read_pickle('results/gurobi_vs_ga.pkl')

plots.plot_travel_time(results_sensitivity)
plots.plot_gurobi_vs_ga(results_gurobi)

# obj, hubs, trips = models.model_a_ga(df, 10, alpha=5/60)
# viz.viz_savings(df, gdf, hubs, trips)

