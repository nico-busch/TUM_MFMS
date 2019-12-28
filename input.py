import pandas as pd
import geopandas as gpd

base = 'https://s3.amazonaws.com/nyc-tlc/trip+data/'
files = ['fhv_tripdata_2019-06.csv',
         'fhvhv_tripdata_2019-06.csv',
         'green_tripdata_2019-06.csv',
         'yellow_tripdata_2019-06.csv']
col_names = [['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID'],
             ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID'],
             ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID'],
             ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID']]
new_names = ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID']
cols = dict(zip(files, col_names))
df = pd.concat((pd.read_csv(base + f, usecols=cols[f], parse_dates=cols[f][:2]).
               rename(columns=dict(zip(cols[f], new_names))) for f in files))
df['ground_travel_time'] = df['dropoff_datetime'] - df['pickup_datetime']
df = df.groupby(['PULocationID', 'DOLocationID']).agg({'ground_travel_time': [pd.Series.mean, 'count']})
df = df.drop([264, 265], level=0).drop([264, 265], level=1)
df = df.reindex(pd.MultiIndex.from_product([range(1, df.index.get_level_values(0).max() + 1),
                                            range(1, df.index.get_level_values(1).max() + 1)],
                                           names=['PULocationID', 'DOLocationID']), fill_value=0)

gdf = gpd.read_file('data/taxi_zones/taxi_zones.shp')
gdf = gdf.set_index('OBJECTID')
gdf = gdf.to_crs({'init': 'epsg:32118'})

centroids = gdf['geometry'].centroid
df['distance'] = df.apply(lambda x: centroids.loc[x.name[0]]
                          .distance(centroids.loc[x.name[1]]), axis=1)
speed = 280000  # avg speed of lilium jet in metres per hour
df['air_travel_time'] = pd.to_timedelta(df['distance'] / speed, 'hours')

df.to_pickle('input.pkl')
