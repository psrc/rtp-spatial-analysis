import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils
import fiona

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

    transit_path = f"{config['user_onedrive']}/{config['rtp_transit_data_path']}"
    transit_routes = gpd.read_file(Path(transit_path)/"Transit_Network_2050_Scenario2b.gdb", layer='transit_routes_2050', engine="fiona")
    transit_routes_frequent = transit_routes[transit_routes['frequent'] == 1]
    transit_routes_frequent = transit_routes_frequent.to_crs(2285)
    # transit_routes = utils.points_in_polygon(transit_routes, cities, "in_city_100ft", buffer=100)
    print(transit_routes_frequent)
    print ('transit routes done')

    layers = fiona.listlayers("C:/Users/ONg/PSRC/GIS - Sharing/Projects/Transportation/RTP_2026/its/ITS_Signals_2024_Final.gdb")
    print(layers)

    signals_path = f"{config['user_onedrive']}/{config['rtp_its_signals_path']}"
    signals = gpd.read_file(Path(signals_path)/"ITS_Signals_2024_Final.gdb", layer='ITS_Signals', engine="fiona")
    signals = signals.to_crs(2285)
    signals.geometry = signals.geometry.buffer(100)
    # signals = utils.points_in_polygon(signals, cities, "in_city_100ft", buffer=100)
    print(signals)
    print ('signals done')
    signals_on_routes = gpd.sjoin(signals, transit_routes_frequent, how="inner", predicate="intersects")
    signals_on_routes = signals_on_routes.drop_duplicates(subset=signals.columns)
    # print(signals_on_routes)
    # combined_gdf = combine_layers(transit_routes_frequent, signals)
    # intersects = combined_gdf.geometry.intersects(transit_routes_frequent = True, signals = True)
    utils.export_layer(signals_on_routes, config, "frequent_transit_routes_and_signal.shp")
    utils.export_csv(signals_on_routes, config, "frequent_transit_routes_and_signal.csv")
    print(signals_on_routes)