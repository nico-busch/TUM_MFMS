import pandas as pd
import gurobipy

df = pd.read_pickle('input.pkl')

demand = df[('ground_travel_time', 'count')].to_numpy()
ground_travel_time = df[('ground_travel_time', 'mean')].to_numpy()
air_travel_time = df['air_travel_time'].to_numpy()