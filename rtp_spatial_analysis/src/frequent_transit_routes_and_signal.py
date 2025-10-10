import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils
import fiona
import pandas as pd

def combine_layers(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""
    buffered_gdf = utils.buffer_layer(line_layer, 500)
    intersected = utils.intersect_layers(buffered_gdf, hex_layer)
    return intersected

def run(config):
    """retrieve fgts and activity units layers, and process them"""

    eg_conn = psrcelmerpy.ElmerGeoConn()
    cities = eg_conn.read_geolayer("cities")
    cities = cities.to_crs(2285) 

    # opening frequent transit routes layer #
    transit_path = f"{config['user_onedrive']}/{config['rtp_transit_data_path']}"
    transit_routes = gpd.read_file(Path(transit_path)/"Transit_Network_2050_Scenario2b.gdb", layer='transit_routes_2050', engine="fiona")
    transit_routes_frequent = transit_routes[transit_routes['frequent'] == 1]
    transit_routes_frequent = transit_routes_frequent.to_crs(2285)
    print(transit_routes_frequent)
    print ('transit routes done') 

    layers = fiona.listlayers("C:/Users/ONg/PSRC/GIS - Sharing/Projects/Transportation/RTP_2026/its/ITS_Signals_2024_Final.gdb")
    print(layers)

    # opening its signals layer #
    signals_path = f"{config['user_onedrive']}/{config['rtp_its_signals_path']}"
    signals = gpd.read_file(Path(signals_path)/"ITS_Signals_2024_Final.gdb", layer='ITS_Signals', engine="fiona")
    signals = signals.to_crs(2285)
    signals.geometry = signals.geometry.buffer(100)
    print(signals)
    print ('signals done')

    # combining frequent transit routes and signals #
    signals_on_routes = gpd.sjoin(signals, transit_routes_frequent, how="inner", predicate="intersects")
    signals_on_routes = signals_on_routes.drop_duplicates(subset=signals.columns)

    num_yes_tsp = (signals_on_routes['tsp'] == 'Yes').sum()
    num_no_tsp = (signals_on_routes['tsp'] == 'No').sum()
    count_rows(num_yes_tsp, num_no_tsp, 'tsp_counts.csv')

    num_yes_ped = (signals_on_routes['ped_signal'] == 'Yes').sum()
    num_no_ped = (signals_on_routes['ped_signal'] == 'No').sum()
    count_rows(num_yes_ped, num_no_ped, 'ped_signal_counts.csv')
   

    utils.export_layer(signals_on_routes, config, "frequent_transit_routes_and_signal.shp")
    utils.export_csv(signals_on_routes, config, "frequent_transit_routes_and_signal.csv")
    print(signals_on_routes)

def count_rows(num_yes, num_no, file_path):
    base_dir = Path('C:/Users/ONg/PSRC/GIS - Sharing/Projects/Transportation/RTP_2026/future_system_output/frequent_transit_routes_signals_output')
    full_path = base_dir/file_path
    counts_df = pd.DataFrame({
        'tsp': ['yes', 'no'],
        'count': [num_yes, num_no]
    })
    # Export to CSV
    counts_df.to_csv(full_path, index=False)
