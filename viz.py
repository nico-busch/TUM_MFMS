import pandas as pd
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter, HoverTool
from bokeh.tile_providers import get_provider, Vendors

def viz_zones(df, gdf):

    output_file('results/zones.html')

    pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
    do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
    vehicle_hrs = ((pu + do) / pd.to_timedelta(1, 'h')).rename('vehicle_hrs')

    gdf = gdf.to_crs({'init': 'epsg:3857'})
    gdf = gdf.join(vehicle_hrs, how='inner')
    gdf = gdf.explode()

    source_zones = GeoJSONDataSource(geojson=gdf.to_json())
    from bokeh.palettes import Viridis256 as palette
    palette.reverse()
    color_mapper = LinearColorMapper(palette=palette[50:], low=gdf['vehicle_hrs'].min(), high=gdf['vehicle_hrs'].max())
    tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
    p = figure(x_axis_location=None, y_axis_location=None)
    p.add_tile(tile_provider)
    zones = p.patches('xs', 'ys', source=source_zones,
                      line_color="white", line_width=0.5,
                      fill_color={'field': 'vehicle_hrs', 'transform': color_mapper},
                      alpha=0.75)
    color_bar = ColorBar(color_mapper=color_mapper,
                         location=(0, 0),
                         orientation='horizontal',
                         major_tick_line_color=None,
                         formatter=NumeralTickFormatter(format='0a'))
    hover = HoverTool(renderers=[zones],
                      tooltips=[('Borough', '@borough'),
                                ('Zone', '@zone'),
                                ('Pickup Vehicle Hours', '@vehicle_hrs{int}')])
    p.add_tools(hover)
    p.add_layout(color_bar, 'below')
    p.hover.point_policy = "follow_mouse"

    show(p)

def viz_hubs(df, gdf, hubs):

    output_file('results/hubs.html')

    pu = (df['ground_travel_time'] * df['n_trips']).groupby(['pickup_location']).sum()
    do = (df['ground_travel_time'] * df['n_trips']).groupby(['dropoff_location']).sum()
    vehicle_hrs = ((pu + do) / pd.to_timedelta(1, 'h')).rename('vehicle_hrs')

    df_air = df.dropna()
    pu_air = (df_air['ground_travel_time'] * df_air['n_trips']).groupby(['pickup_location']).sum()
    do_air = (df_air['ground_travel_time'] * df_air['n_trips']).groupby(['dropoff_location']).sum()
    vehicle_hrs_air = ((pu_air + do_air) / pd.to_timedelta(1, 'h')).rename('vehicle_hrs_air')

    gdf = gdf.to_crs({'init': 'epsg:3857'})
    gdf = gdf.join(vehicle_hrs, how='right')
    gdf_hubs = gdf.loc[hubs]
    gdf_hubs['geometry'] = gdf_hubs.centroid
    gdf_hubs = gdf_hubs.join(vehicle_hrs_air / vehicle_hrs_air.max() * 15, how='left')
    gdf = gdf.explode()

    source_zones = GeoJSONDataSource(geojson=gdf.to_json())
    source_hubs = GeoJSONDataSource(geojson=gdf_hubs.to_json())
    from bokeh.palettes import Viridis256 as palette
    palette.reverse()
    color_mapper = LinearColorMapper(palette=palette[50:], low=gdf['vehicle_hrs'].min(), high=gdf['vehicle_hrs'].max())
    tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
    p = figure(x_axis_location=None, y_axis_location=None)
    p.add_tile(tile_provider)
    zones = p.patches('xs', 'ys', source=source_zones,
                      line_color="white", line_width=0.5,
                      fill_color={'field': 'vehicle_hrs', 'transform': color_mapper},
                      alpha=0.75)
    p.circle('x', 'y', source=source_hubs, size='vehicle_hrs_air', color="darkorange")
    color_bar = ColorBar(color_mapper=color_mapper,
                         location=(0, 0),
                         orientation='horizontal',
                         major_tick_line_color=None,
                         formatter=NumeralTickFormatter(format='0a'))
    hover = HoverTool(renderers=[zones],
                      tooltips=[('Borough', '@borough'),
                                ('Zone', '@zone'),
                                ('Total Vehicle Hours', '@vehicle_hrs{int}')])
    p.add_tools(hover)
    p.add_layout(color_bar, 'below')
    p.hover.point_policy = "follow_mouse"

    show(p)
