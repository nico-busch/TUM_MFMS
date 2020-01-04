import numpy as np
import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter, HoverTool
from bokeh.palettes import Viridis8 as palette
from bokeh.tile_providers import get_provider, Vendors

df = pd.read_pickle('input.pkl')

n_zones = 25
df = pd.read_pickle('input.pkl')
pu = (df['ground_travel_time'] * df['n_trips']).groupby(['PULocationID']).sum()
do = (df['ground_travel_time'] * df['n_trips']).groupby(['DOLocationID']).sum()
zones = (pu + do).nlargest(n_zones).index.sort_values()
df = df.loc[(zones, zones), :]
routes = df.index
shape = routes.remove_unused_levels().levshape

pu = df.groupby(['PULocationID']).agg({'n_trips': 'sum'})
pu.columns = ['pu_count']
do = df.groupby(['DOLocationID']).agg({'n_trips': 'sum'})
do.columns = ['do_count']

gdf = gpd.read_file('https://s3.amazonaws.com/nyc-tlc/misc/taxi_zones.zip')
gdf = gdf.set_index('OBJECTID')
gdf = gdf.to_crs({'init': 'epsg:3857'})
gdf = gdf.join(pu, how='inner')
gdf = gdf.join(do, how='inner')
gdf['sum'] = gdf['pu_count'] + gdf['do_count']
#gdf = gdf.explode()
loc = np.loadtxt('hubs.csv', dtype=int)
hubs = gdf.loc[loc].centroid

source_zones = GeoJSONDataSource(geojson=gdf.to_json())
source_hubs = GeoJSONDataSource(geojson=hubs.to_json())
palette.reverse()
color_mapper = LinearColorMapper(palette=palette[3:], low=0, high=1e6)
tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
p = figure(x_axis_location=None, y_axis_location=None)
p.add_tile(tile_provider)
zones = p.patches('xs', 'ys', source=source_zones,
                  line_color="white", line_width=0.5,
                  fill_color={'field': 'sum', 'transform': color_mapper},
                  alpha=0.75)
hubs = p.circle('x', 'y', size=10, source=source_hubs, color="orange")
hover = HoverTool(renderers=[zones],
                  tooltips=[('Borough', '@borough'),
                            ('Zone', '@zone'),
                            ('Pickups', '@pu_count'),
                            ('Dropoffs', '@do_count')])
color_bar = ColorBar(color_mapper=color_mapper,
                     location=(0, 0),
                     orientation='horizontal',
                     major_tick_line_color=None,
                     formatter=NumeralTickFormatter(format='0a'))
p.add_layout(color_bar, 'below')
p.hover.point_policy = "follow_mouse"
show(p)
