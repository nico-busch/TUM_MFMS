import pandas as pd
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, LogColorMapper, ColorBar, NumeralTickFormatter, HoverTool
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
                                ('Total Vehicle Hours', '@vehicle_hrs{int}')])
    p.add_tools(hover)
    p.add_layout(color_bar, 'below')
    p.hover.point_policy = "follow_mouse"

    show(p)

def viz_hubs(gdf, hubs, trips):

    output_file('results/hubs.html')

    pu = (trips.loc[trips['hubs'].notna(), 'travel_time']
          * trips.loc[trips['hubs'].notna(), 'n_trips']).groupby(['pickup_location']).sum()
    do = (trips.loc[trips['hubs'].notna(), 'travel_time']
          * trips.loc[trips['hubs'].notna(), 'n_trips']).groupby(['dropoff_location']).sum()
    vehicle_hrs = (pu.add(do, fill_value=0) / pd.to_timedelta(1, 'h')).rename('vehicle_hrs')

    gdf = gdf.to_crs({'init': 'epsg:3857'})
    gdf = gdf.join(vehicle_hrs, how='right')
    gdf_hubs = gdf.loc[hubs]
    gdf_hubs['geometry'] = gdf_hubs.centroid
    gdf = gdf.explode()

    palette = linear_gradient('#bfe1ff', '#0065bd', n=50) + linear_gradient('#0065bd', '#00335f', n=200)
    source_zones = GeoJSONDataSource(geojson=gdf.to_json())
    source_hubs = GeoJSONDataSource(geojson=gdf_hubs.to_json())
    color_mapper = LinearColorMapper(palette=palette, low=vehicle_hrs.min(), high=vehicle_hrs.max())
    tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
    p = figure(x_axis_location=None, y_axis_location=None)
    p.add_tile(tile_provider)
    zones = p.patches('xs', 'ys', source=source_zones,
                      line_color="white", line_width=0.5,
                      fill_color={'field': 'vehicle_hrs', 'transform': color_mapper},
                      alpha=0.75)
    p.circle('x', 'y', source=source_hubs, size=10, color="darkorange")
    color_bar = ColorBar(color_mapper=color_mapper,
                         location=(0, 0),
                         orientation='horizontal',
                         major_tick_line_color=None,
                         formatter=NumeralTickFormatter(format='0a'))
    hover = HoverTool(renderers=[zones],
                      tooltips=[('Borough', '@borough'),
                                ('Zone', '@zone'),
                                ('Air Travel Vehicle Hours', '@vehicle_hrs{int}')])
    p.add_tools(hover)
    p.add_layout(color_bar, 'below')
    p.hover.point_policy = "follow_mouse"

    show(p)

def hex_to_RGB(hex):
    return [int(hex[i:i + 2], 16) for i in range(1, 6, 2)]

def RGB_to_hex(RGB):
    RGB = [int(x) for x in RGB]
    return "#" + "".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB])

def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10):
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    hex_list = [start_hex]
    for t in range(1, n):
        curr_vector = [int(s[j] + (float(t) / (n - 1)) * (f[j] - s[j])) for j in range(3)]
        hex_list.append(RGB_to_hex(curr_vector))
    return hex_list

def viz_savings(df, gdf, hubs, trips):

    output_file('results/hubs.html')

    temp = (df['ground_travel_time'] - trips['travel_time']).loc[trips['hubs'].notna()]
    temp[temp > pd.to_timedelta(3, 'h')] = pd.to_timedelta(0, 'h')
    temp = temp * df['n_trips']
    diff = (temp.groupby(['pickup_location']).sum() + temp.groupby(['dropoff_location']).sum()) \
           / (df['n_trips'].groupby(['pickup_location']).sum() + df['n_trips'].groupby(['dropoff_location']).sum())
    savings = (diff / pd.to_timedelta(1, 'm')).rename('savings')

    gdf = gdf.to_crs({'init': 'epsg:3857'})
    gdf = gdf.join(savings, how='right')
    gdf_hubs = gdf.loc[hubs]
    gdf_hubs['geometry'] = gdf_hubs.centroid
    gdf = gdf.explode()

    # palette = linear_gradient('#bfe1ff', '#0065bd', n=50) + linear_gradient('#0065bd', '#00335f', n=200)
    palette = linear_gradient('#bfe1ff', '#00335f', n=256)
    source_zones = GeoJSONDataSource(geojson=gdf.to_json())
    source_hubs = GeoJSONDataSource(geojson=gdf_hubs.to_json())
    color_mapper = LogColorMapper(palette=palette, low=savings.min(), high=savings.max())
    tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)
    p = figure(x_axis_location=None, y_axis_location=None)
    p.add_tile(tile_provider)
    zones = p.patches('xs', 'ys', source=source_zones,
                      line_color="white", line_width=0.5,
                      fill_color={'field': 'savings', 'transform': color_mapper},
                      alpha=0.75)
    p.circle('x', 'y', source=source_hubs, size=10, color="darkorange")
    color_bar = ColorBar(color_mapper=color_mapper,
                         location=(0, 0),
                         orientation='horizontal',
                         major_tick_line_color=None,
                         formatter=NumeralTickFormatter(format='0a'))
    hover = HoverTool(renderers=[zones],
                      tooltips=[('Borough', '@borough'),
                                ('Zone', '@zone'),
                                ('Air Travel Savings', '@savings')])
    p.add_tools(hover)
    p.add_layout(color_bar, 'below')
    p.hover.point_policy = "follow_mouse"

    show(p)
