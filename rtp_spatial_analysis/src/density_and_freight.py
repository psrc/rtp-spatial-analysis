import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils

def combine_layers(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""
    buffered_gdf = utils.buffer_layer(line_layer, 500)
    intersected = utils.intersect_layers(buffered_gdf, hex_layer)
    return intersected

def export_shp(gdf):
    """export to a pre-defined file location"""
    pth = Path("C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp")
    gdf.to_file(pth)

def sum_combined(gdf):
    c = gdf[['GRID_ID', 
            'sum_pop_20', 
            'sum_jobs_2', 
            'sum_au_205', 
            'jobs_acre', 
            'pop_acre', 
            'au_acre', 
            'geometry']].copy()

    c['acreage'] = c['geometry'].area / 43560 # calculate acreage for new polygons
    c['au'] = c['au_acre'].fillna(0) * c['acreage'].fillna(0) # calculate au for acreage
    s = c.au.sum() # sum the pop, jobs and au's
    return(s)

def run(config):
    """retrieve fgts and activity units layers, and process them"""
    path_to_fgtwa = f"{config['user_onedrive']}/{config['fgtswa_path']}"
    fgtswa = gpd.read_file(Path(path_to_fgtwa), layer='FGTSWA')
    fgtswa = fgtswa.to_crs(2285)

    activity_units_full_path = f"{config['user_onedrive']}/{config['activity_units_path']}"
    activity_units_2050 = gpd.read_file(Path(activity_units_full_path), layer='peope_and_jobs_2050')
    activity_units_2050 = activity_units_2050.to_crs(2285)

    combined_gdf = combine_layers(fgtswa, activity_units_2050)
    #utils.export_layer(combined_gdf, config, "fgts_and_density_2050.shp")

    total_au = activity_units_2050.sum_au_205.sum()
    print(f"total activity units in region: {total_au}.")

    summed = sum_combined(combined_gdf)
    print(f"activity units within buffer: {summed}.")
    print(f"done density_and_freight")
