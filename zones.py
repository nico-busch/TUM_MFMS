import geopandas as gpd
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource, LogColorMapper
from bokeh.palettes import Inferno10 as palette
from bokeh.tile_providers import get_provider, Vendors
import pandas as pd

df = pd.read_pickle('input.pkl')
df = df.groupby(['PULocationID']).agg({('ground_travel_time', 'count'): 'sum'})
df.columns = ['count']

gdf = gpd.read_file('data/taxi_zones/taxi_zones.shp')
gdf = gdf.set_index('OBJECTID')
gdf = gdf.to_crs({'init': 'epsg:3857'})
gdf = gdf.join(df, how='inner')

source = GeoJSONDataSource(geojson=gdf.to_json())
palette.reverse()
tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
color_mapper = LogColorMapper(palette=palette)
p = figure(title='New York Taxi Pickups',
           x_axis_location=None, y_axis_location=None,
           tooltips=[('Borough', '@borough'), ('Zone', '@zone'), ('Pickups', '@count')])
p.add_tile(tile_provider)

zones = p.patches('xs', 'ys', source=source,
                  line_color="white", line_width=0.5,
                  fill_color={'field': 'count', 'transform': color_mapper},
                  alpha=0.75)
p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"
show(p)