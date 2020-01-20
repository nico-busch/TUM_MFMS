import numpy as np
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

    date_parser = lambda x: pd.to_datetime(x, errors='coerce')
    df = pd.concat((pd.read_csv(base + f, usecols=cols[f], parse_dates=cols[f][:2], date_parser=date_parser)
                   .rename(columns=dict(zip(cols[f], new_names))) for f in files))
    df = df.dropna()
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

    idx = df.index.get_level_values(0).unique().union(df.index.get_level_values(0).unique())
    df = df.reindex(pd.MultiIndex.from_product([idx, idx], names=df.index.names), fill_value=0)

    df.to_pickle('data/trips_ny.pkl')
    gdf.to_pickle('data/zones_ny.pkl')

    return df, gdf


def input_chicago():

    cols = ['trip_start_timestamp', 'trip_end_timestamp', 'pickup_community_area', 'dropoff_community_area']
    new_names = ['pickup_datetime', 'dropoff_datetime', 'pickup_location', 'dropoff_location']

    date_parser = lambda x: pd.to_datetime(x, errors='coerce')
    n_rows = 1000000
    df = pd.read_csv('https://data.cityofchicago.org/resource/wrvz-psew.csv?%24limit=' + str(n_rows),
                     usecols=cols,
                     parse_dates=cols[:2], date_parser=date_parser).rename(columns=dict(zip(cols, new_names)))
    df = df.dropna()
    df = df.astype(dict(zip(new_names[2:], [np.int64, np.int64])))
    df['ground_travel_time'] = df['dropoff_datetime'] - df['pickup_datetime']
    df = df.groupby(['pickup_location', 'dropoff_location']).agg({'ground_travel_time': [pd.Series.mean, 'count']})
    df.columns = ['ground_travel_time', 'n_trips']
    df.loc[df.index.get_level_values(0) == df.index.get_level_values(1), 'ground_travel_time'] = pd.to_timedelta(0)

    gdf = gpd.read_file('https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON')
    gdf = gdf.set_index('area_num_1')
    gdf.index = gdf.index.astype(np.int64)
    gdf = gdf.to_crs({'init': 'epsg:26971'})
    centroids = gdf['geometry'].centroid

    df['distance'] = df.apply(lambda x: centroids.loc[x.name[0]]
                              .distance(centroids.loc[x.name[1]]), axis=1)
    speed = 280000  # avg speed of lilium jet in metres per hour
    df['air_travel_time'] = pd.to_timedelta(df['distance'] / speed, 'h')
    df = df.drop('distance', 1)

    idx = df.index.get_level_values(0).unique().union(df.index.get_level_values(0).unique())
    df = df.reindex(pd.MultiIndex.from_product([idx, idx], names=df.index.names), fill_value=0)

    df.to_pickle('data/trips_chicago.pkl')
    gdf.to_pickle('data/zones_chicago.pkl')
