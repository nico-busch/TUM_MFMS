import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import Viridis8 as palette
from bokeh.tile_providers import get_provider, Vendors

df = pd.read_pickle('input.pkl')
pu = df.groupby(['PULocationID']).agg({('ground_travel_time', 'count'): 'sum'})
pu.columns = ['pu_count']
do = df.groupby(['DOLocationID']).agg({('ground_travel_time', 'count'): 'sum'})
do.columns = ['do_count']

gdf = gpd.read_file('https://s3.amazonaws.com/nyc-tlc/misc/taxi_zones.zip')
gdf = gdf.set_index('OBJECTID')
gdf = gdf.to_crs({'init': 'epsg:3857'})
gdf = gdf.join(pu, how='inner')
gdf = gdf.join(do, how='inner')
gdf['sum'] = gdf['pu_count'] + gdf['do_count']
gdf = gdf.explode()

source = GeoJSONDataSource(geojson=gdf.to_json())
palette.reverse()
color_mapper = LinearColorMapper(palette=palette[3:], low=0, high=1e6)
tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
p = figure(x_axis_location=None, y_axis_location=None,
           tooltips=[('Borough', '@borough'), ('Zone', '@zone'), ('Pickups', '@pu_count'), ('Dropoffs', '@do_count')],)
p.add_tile(tile_provider)
zones = p.patches('xs', 'ys', source=source,
                  line_color="white", line_width=0.5,
                  fill_color={'field': 'sum', 'transform': color_mapper},
                  alpha=0.75)
color_bar = ColorBar(color_mapper=color_mapper,
                     location=(0, 0),
                     orientation='horizontal',
                     major_tick_line_color=None,
                     formatter=NumeralTickFormatter(format='0a'))
p.add_layout(color_bar, 'below')
p.hover.point_policy = "follow_mouse"
show(p)
