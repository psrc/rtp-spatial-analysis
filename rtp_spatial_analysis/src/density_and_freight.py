import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils

def combine_layers(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""
    buffered_gdf = utils.buffer_layer(line_layer, 500)
    intersected = utils.intersect_layers(buffered_gdf, hex_layer)
    return intersected

def run(config):
    """retrieve fgts and activity units layers, and process them"""
    path_to_fgtwa = f"{config['user_onedrive']}/{config['fgtswa_path']}"
    fgtswa = gpd.read_file(Path(path_to_fgtwa), layer='FGTSWA')
    print('read fgtswa')
    fgtswa = fgtswa.to_crs(2285)

    activity_units_full_path = f"{config['user_onedrive']}/{config['activity_units_path']}"
    activity_units_2050 = gpd.read_file(Path(activity_units_full_path), layer='peope_and_jobs_2050')
    print('read activity_units')
    activity_units_2050 = activity_units_2050.to_crs(2285)

    combined_gdf = combine_layers(fgtswa, activity_units_2050)
    utils.export_layer(combined_gdf, config, "fgts_and_density_2050.shp")

    print(combined_gdf)
    print("done")
