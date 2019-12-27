import pandas as pd
import geopandas as gpd

df = pd.read_csv('data/yellow_tripdata_2019-06.csv', parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
df['ground_travel_time'] = df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
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
