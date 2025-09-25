import geopandas as gpd
import psrcelmerpy
from pathlib import Path 



def buffer_layer(layer_gdf, distance):
    if distance > 0:
        buffered_gdf = layer_gdf.copy()
        buffered_gdf.geometry = buffered_gdf.geometry.buffer(distance)
    return buffered_gdf

def intersect_layers(df1, df2, how='intersection'):
    return df1.overlay(df2, how= how)

def points_in_polygon(points_gdf, polygons_gdf, col_name, buffer=0):
    """Check if a point intersects a polygon with an optional buffer, and add a boolean column."""
    if buffer > 0:
        buffered_points_gdf = points_gdf.copy()
        buffered_points_gdf.geometry = buffered_points_gdf.geometry.buffer(buffer)
        intersects = buffered_points_gdf.geometry.intersects(polygons_gdf.geometry.unary_union)
    else:
        intersects = points_gdf.geometry.intersects(polygons_gdf.geometry.unary_union)
    points_gdf[col_name] = intersects
    return points_gdf

def export_layer(gdf, config, lyr_nm):
    """export to a pre-defined file location"""
    path_to_output = f"{config['user_onedrive']}/{config['rtp_output_path']}"
    pth = Path(path_to_output, lyr_nm)
    gdf.to_file(pth)
