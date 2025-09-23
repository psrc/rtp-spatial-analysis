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

