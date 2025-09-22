import geopandas as gpd
import psrcelmerpy
from pathlib import Path 

def buffer_layer(layer_gdf, buffer):
    if buffer > 0:
        buffered_gdf = layer_gdf.copy()
        buffered_gdf.geometry = buffered_gdf.geometry.buffer(buffer)
    return buffered_gdf


def intersect_layers(buffered_line_gdf, polygon_gdf):
    return buffered_line_gdf.overlay(polygon_gdf, how='intersection')


def combine_layers(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""
    buffered_gdf = buffer_layer(line_layer, 500)
    intersected = intersect_layers(buffered_gdf, hex_layer)
    return intersected

def export_shp(gdf):
    """export to a pre-defined file location"""
    pth = Path("C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp")
    gdf.to_file(pth)

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

    export_shp(combined_gdf)
    print(combined_gdf)
    print("done")
