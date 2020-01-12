import pandas as pd
import geopandas as gpd

def input_ny():

    base = 'https://s3.amazonaws.com/nyc-tlc/trip+data/'
    files = ['fhv_tripdata_2019-03.csv',
             'fhvhv_tripdata_2019-03.csv',
             'green_tripdata_2019-03.csv',
             'yellow_tripdata_2019-03.csv']
    col_names = [['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID'],
                 ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID'],
                 ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID'],
                 ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID']]
    new_names = ['pickup_datetime', 'dropoff_datetime', 'pickup_location', 'dropoff_location']
    cols = dict(zip(files, col_names))

    df = pd.concat((pd.read_csv(base + f, usecols=cols[f], parse_dates=cols[f][:2])
                   .rename(columns=dict(zip(cols[f], new_names))) for f in files))
    df['ground_travel_time'] = df['dropoff_datetime'] - df['pickup_datetime']
    df = df.groupby(['pickup_location', 'dropoff_location']).agg({'ground_travel_time': [pd.Series.mean, 'count']})
    df.columns = ['ground_travel_time', 'n_trips']
    df.loc[df.index.get_level_values(0) == df.index.get_level_values(1), 'ground_travel_time'] = pd.to_timedelta(0)
    # zones 264 and 265 do not exist
    df = df.drop([264, 265], level=0).drop([264, 265], level=1)

    gdf = gpd.read_file('https://s3.amazonaws.com/nyc-tlc/misc/taxi_zones.zip')
    gdf = gdf.set_index('OBJECTID')
    gdf = gdf.to_crs({'init': 'epsg:32118'})
    centroids = gdf['geometry'].centroid

    df['distance'] = df.apply(lambda x: centroids.loc[x.name[0]]
                              .distance(centroids.loc[x.name[1]]), axis=1)
    speed = 280000  # avg speed of lilium jet in metres per hour
    df['air_travel_time'] = pd.to_timedelta(df['distance'] / speed, 'h')
    df = df.drop('distance', 1)

    df.to_pickle('data/trips_ny.pkl')
    gdf.to_pickle('data/zones_ny.pkl')


def input_chicago():

    gdf = gpd.read_file('https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON')
    gdf = gdf.to_crs({'init': 'epsg:26971'})
