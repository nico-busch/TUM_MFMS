import geopandas as gpd
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource

gdf = gpd.read_file('data/taxi_zones/taxi_zones.shp')
gdf = gdf.set_index('OBJECTID')
gdf = gdf.to_crs({'init': 'epsg:32118'})

source = GeoJSONDataSource(geojson=gdf.to_json())
p = figure(title='test',
           x_axis_label='x', y_axis_label='y',
           tooltips=[('Borough', '@borough'), ('Zone', '@zone')])

zones = p.patches('xs', 'ys', source=source, line_color="white", line_width=0.5)
p.hover.point_policy = "follow_mouse"
show(p)