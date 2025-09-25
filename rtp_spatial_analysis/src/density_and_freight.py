import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils

def combine_layers(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""
    try:
        buffered_gdf = utils.buffer_layer(line_layer, 500)
        intersected = utils.intersect_layers(buffered_gdf, hex_layer)
        return intersected
    except Exception as e:
        print(f"Error in combine_layers: {e}")
        raise

def export_shp(gdf):
    """export to a pre-defined file location"""
    try:
        pth = Path("C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp")
        gdf.to_file(pth)
    except Exception as e:
        print(f"Error in export_shp: {e}")
        raise

def sum_combined(gdf):
    try:
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
    except Exception as e:
        print(f"Error in sum_combined: {e}")
        raise

    

def run(config):
    """retrieve fgts and activity units layers, and process them"""
    try:

        fgtswa = utils.get_onedrive_layer(config, 'fgtswa_path', 'FGTSWA')
        activity_units_2050 = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')
        combined_gdf = combine_layers(fgtswa, activity_units_2050)
        #utils.export_layer(combined_gdf, config, "fgts_and_density_2050.shp")

        total_au = activity_units_2050.sum_au_205.sum()
        print(f"total activity units in region: {total_au}.")

        summed = sum_combined(combined_gdf)
        print(f"activity units within buffer: {summed}.")
        print(f"done density_and_freight")
    except Exception as e:
        print(f"Error in run: {e}")
        raise
