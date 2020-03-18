import pandas as pd
import numpy as np
import models
from bokeh.io import output_file
from bokeh.plotting import figure, show
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter, HoverTool
from bokeh.tile_providers import get_provider, Vendors
import seaborn as sns
import matplotlib.pyplot as plt # due to release problems older version is needed -> downgrade to 3.1.0

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

    gdf = gdf.to_crs({'init': 'epsg:3857'})
    gdf = gdf.join(vehicle_hrs, how='right')
    gdf_hubs = gdf.loc[hubs]
    gdf_hubs['geometry'] = gdf_hubs.centroid
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
    p.circle('x', 'y', source=source_hubs, size=10, color="darkorange")
    color_bar = ColorBar(color_mapper=color_mapper,
                         location=(0, 0),
                         orientation='horizontal',
                         major_tick_line_color=None,
                         formatter=NumeralTickFormatter(format='0a'))
    hover = HoverTool(renderers=[zones],
                      tooltips=[('Borough', '@borough'),
                                ('Zone', '@zone'),
                                ('Zone', '@zone'),
                                ('Total Vehicle Hours', '@vehicle_hrs{int}')])
    p.add_tools(hover)
    p.add_layout(color_bar, 'below')
    p.hover.point_policy = "follow_mouse"

    show(p)

def viz_connection_heatmap(n_hubs, n_zones=263, alpha=0, beta=1):
    # run Genetic Algorithm
    data_ = prepare_data(n_zones)
    _, _, df = models.model_a_ga(data_, n_hubs,  alpha=alpha, beta=beta)

    # create data
    df_hubs = trip_count_df(df)

    # plot heatmap
    df_ = df_hubs.copy()
    df_['trip_count'] = (df_['trip_count'] / 1000).astype(int)
    df_ = df_.reset_index().pivot(columns='destination', index='origin', values='trip_count')
    df_ = df_.fillna(0)
    df_ = df_.astype(int)
    mask = np.ones_like(df_)

    mask[np.tril_indices_from(df_)] = False

    fig, ax = plt.subplots(1, 1, figsize = (15, 15))
    sns.heatmap(df_, cmap="YlGnBu", annot=True, fmt='', mask=mask, square=True, linewidths=1,
                cbar_kws={'label': 'Number of trips [k]'})
    ax.set_ylabel('')
    ax.set_xlabel('')
    plt.show()

def viz_hub_importance(n_hubs, n_zones=263, alpha=0, beta=1):
    # run Genetic Algorithm
    data_ = prepare_data(n_zones)
    _, hubs, df = models.model_a_ga(data_, n_hubs,  alpha=alpha, beta=beta)

    # create data
    df_hubs = trip_count_df(df)
    df_ = hub_importance(hubs, df_hubs)

    # donut plot
    fig, ax = plt.subplots(1, 1, figsize=(15, 15))
    df_ = df_.drop(columns='hubs_')
    ax = df_.plot.bar(rot=0, cmap="Set3")
    ax.set_ylabel('Number of trips per month [k]')
    ax.set_xlabel('')
    ax.get_legend().remove()
    plt.show()

    '''
    fig, ax = plt.subplots(1, 1, figsize = (15, 15))
    circle = plt.Circle((0, 0), 0.7, color='white')
    ax.pie(df_['trip_count'], labels=df_['hubs_'], wedgeprops={'linewidth': 7, 'edgecolor': 'white'})
    ax.add_artist(circle)
    #axs[k, l].set_title('Number of hubs: ' + str(h_[count_ - 1]))
    '''
    plt.show()

def viz_hub_utilization(n_hubs, n_zones=263, alpha=0, beta=1):

    data_ = prepare_data(n_zones)

    df_total = pd.DataFrame(columns=['trips_per_hub', 'trip_type', 'trip_count', 'p', 'percentage'])
    df_total_2 = pd.DataFrame(columns=['p', 'trips_per_hub'])

    for i in range(n_hubs + 1):
        if (i >= 2):

            # run Genetic Algorithm
            _, hubs, df = models.model_a_ga(data_, i, alpha=alpha, beta=beta)

            # adding trip transfer types information to df
            df['trip_type'] = 'non_air'
            for index, row in df.dropna().iterrows():
                tmp = tuple(row['hubs'])
                if ((tmp[0] == index[0] and tmp[1] == index[1]) or (tmp[0] == index[1] and tmp[1] == index[0])):
                    df.loc[index, 'trip_type'] = 'direct'
                elif (tmp[0] == index[0] or tmp[1] == index[1] or tmp[1] == index[0] or tmp[0] == index[1]):
                    df.loc[index, 'trip_type'] = 'one_transfer'
                else:
                    df.loc[index, 'trip_type'] = 'two_transfer'

            un = np.array(['direct', 'one_transfer', 'two_transfer'])
            df_ = pd.DataFrame(data=un.flatten(), columns=['trip_type'])
            df_['trip_count'] = np.NAN
            df_['p'] = i
            df_['percentage'] = df[df['trip_type'] != 'non_air']['n_trips'].sum()
            count = 0
            for ii in un:
                df_.loc[count, 'trip_count'] = df[df['trip_type'] == ii]['n_trips'].sum()
                df_.loc[count, 'percentage'] = df_.loc[count, 'trip_count'] / df_.loc[count, 'percentage']
                df_.loc[count, 'trips_per_hub'] = df[df['trip_type'] != 'non_air']['n_trips'].sum() / i
                count = count + 1
            df_total = df_total.append(df_, ignore_index=True)


            tph = df[df['trip_type'] != 'non_air']['n_trips'].sum() / i
            df2 = pd.DataFrame([[i, tph]], columns=['p', 'trips_per_hub'])
            df_total_2 = df_total_2.append(df2, ignore_index=True)


    # plot

    print(df_total)

    colors = ["#006D2C", "#31A354", "#74C476"]
    pivot_df = df_total.pivot(index='p', columns='trip_type', values='trip_count')
    pivot_df.plot.bar(stacked=True, color=colors)

    df_total_2 = df_total_2.set_index('p')
    df_total_2.plot(style='.-')

    plt.show()

def viz_time_savings_boxplot(n_hubs=[3,5,7,9], n_zones=263, alpha=0, beta=1):
    # data preperation
    data = pd.read_pickle('data/trips_ny.pkl')
    total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
            (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
    zones = total.nlargest(n_zones).index.sort_values()
    data_ = data.loc[(zones, zones), :]
    data_.index = data_.index.remove_unused_levels()
    data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)
    '''
    time_savings_data = pd.DataFrame(columns=n_hubs)
    for i in n_hubs:
        _, hubs, df = models.model_a_ga(data_, 9, alpha=alpha, beta=beta)
        temp = (data_['ground_travel_time'] - df['travel_time']).loc[df['hubs'].notna()]
        temp[temp > pd.to_timedelta(3, 'h')] = pd.to_timedelta(0, 'h')
        temp[temp <= pd.to_timedelta(0, 'h')] = np.NaN
        temp = temp.dropna()
        savings = (temp / pd.to_timedelta(1, 'm')).rename('savings')
        time_savings_data[''+str(i)] = savings
        time_savings_data.to_pickle('results/time_saving_data.pkl')
    '''
    time_savings_data = pd.read_pickle('results/histogram_data.pkl')
    df =  time_savings_data
    df.boxplot()
    plt.xlabel('Number of hubs')
    plt.ylabel('Time savings [min]')
    plt.show()

def viz_time_savings_histogram(n_hubs=[3,5,7,9], n_zones=263, alpha=5/60, beta=1):
    # data preperation
    data = pd.read_pickle('data/trips_ny.pkl')
    total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
            (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
    zones = total.nlargest(n_zones).index.sort_values()
    data_ = data.loc[(zones, zones), :]
    data_.index = data_.index.remove_unused_levels()
    data_ = data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)
    '''
    histogram_time_savings_data = pd.DataFrame(columns=n_hubs)
    for i in n_hubs:
        _, hubs, df = models.model_a_ga(data_, 9, alpha=alpha, beta=beta)
        temp = (data_['ground_travel_time'] - df['travel_time']).loc[df['hubs'].notna()]
        temp[temp > pd.to_timedelta(3, 'h')] = pd.to_timedelta(0, 'h')
        temp[temp <= pd.to_timedelta(0, 'h')] = np.NaN
        temp = temp.dropna()
        savings = (temp / pd.to_timedelta(1, 'm')).rename('savings')
        histogram_time_savings_data[''+str(i)] = savings
        histogram_time_savings_data.to_pickle('results/histogram_data.pkl')
    '''
    histogram_time_savings_data = pd.read_pickle('results/histogram_data.pkl')
    df =  histogram_time_savings_data

    # histogram
    ncols = 2
    nrows = int(np.ceil(len(df.columns) / (1.0 * ncols)))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
    counter = 0
    title_c = 0
    for i in range(nrows):
        for j in range(ncols):
            ax = axes[i][j]
            # Plot when we have data
            if counter < len(df.columns):
                ax.hist(df[df.columns[counter]], color='skyblue', alpha=0.8, label='{}'.format(df.columns[counter]))
                ax.set_xlabel('Time savings [min]')
                ax.set_ylabel('Number of trips')
                ax.set_title('' + str(n_hubs[title_c]) + ' hubs')
                title_c = title_c + 1
                ax.set_ylim([0, 800])
                ax.set_xlim([0, 130])
            # Remove axis when we no longer have data
            else:
                ax.set_axis_off()
            counter += 1
    fig.tight_layout()
    plt.show()

#-----------------------------------------------------------------------------------------------------------------------
# Supportive functions

def prepare_data(n_zones):
    # data preperation
    data = pd.read_pickle('data/trips_ny.pkl')
    total = (data['ground_travel_time'] * data['n_trips']).groupby(['pickup_location']).sum() + \
            (data['ground_travel_time'] * data['n_trips']).groupby(['dropoff_location']).sum()
    zones = total.nlargest(n_zones).index.sort_values()
    data_ = data.loc[(zones, zones), :]
    data_.index = data_.index.remove_unused_levels()
    return data_.reindex(pd.MultiIndex.from_product([zones, zones], names=data_.index.names), fill_value=0)

def trip_count_df(df):
    # create df_hubs for counting all trips going through a hub connection
    un = df['hubs'].unique()
    un = np.delete(un, 0)  # delete nan value
    df_hubs = pd.DataFrame(data=un.flatten(), columns=['hubs'])
    df_hubs = df_hubs.set_index('hubs')
    df_hubs['trip_count'] = 0
    for index, row in df_hubs.iterrows():
        df_hubs.loc[index, 'trip_count'] = df.loc[df['hubs'] == tuple(index)]['n_trips'].sum()
    df_hubs.index = pd.MultiIndex.from_tuples(df_hubs.index, names=('origin', 'destination'))
    df_hubs.index = df_hubs.index.drop_duplicates(keep='first')

    # aggregate both demand direction of a hub connection to one single value
    tmp = df_hubs.copy()
    existing_indexes = []
    for index, row in df_hubs.iterrows():
        df_hubs.loc[index] = tmp.loc[index] + tmp.loc[(index[1], index[0])] + 0
    return df_hubs

def hub_importance(hubs, df_hubs):
    # create dataframe representing the hub importance (number of trips)
    df_ = pd.DataFrame(data=hubs.flatten(), columns=['hubs'])
    df_['trip_count'] = 0
    df_['hubs_'] = df_['hubs']
    df_ = df_.set_index('hubs')
    for i in hubs:
        for j in hubs:
            if (i != j):
                df_.loc[(i), 'trip_count'] = df_.loc[(i), 'trip_count'] + df_hubs.loc[(i, j), 'trip_count']

    df_['trip_count'] = df_['trip_count'] / 1000
    return df_.sort_values(by=['trip_count'])