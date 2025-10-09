import pandas as pd
import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils


def buffer_and_combine(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""

    try:
        buffered_gdf = buffer_layer(line_layer, 500)
        intersected = intersect_layers(buffered_gdf, hex_layer)
        return intersected

    except Exception as e:
        print(f"Error in buffer_and_combine: {e}")
        raise

def export_shp(gdf):
    """export to a pre-defined file location"""

    try:
        pth = Path("C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp")
        gdf.to_file(pth)

    except Exception as e:
        print(f"Error in export_shp: {e}")
        raise


def sum_combined(gdf, config):
    """
    Get a sum of activity units in a geodataframe
    
    Args:
        A gdf with columns "geometry" and "au_acre" (activity units per acre) 

    Returns: 
        An integer representing the summed activity units in the gdf
    """
    try:
        c = gdf[['GRID_ID', 
                'sum_au_205', 
                'au_acre', 
                'geometry']].copy()

        acre_in_sqft = config['acre_in_sqft']
        c['acreage'] = c['geometry'].area / acre_in_sqft # calculate acreage for new polygons
        c['au'] = c['au_acre'].fillna(0) * c['acreage'].fillna(0) # calculate au for acreage
        s = c.au.sum() # sum the au's
        return(s)

    except Exception as e:
        print(f"Error in sum_combined: {e}")
        raise


def run(config):
    """
    Get density within 500 feet of FGTS Routes
    
    Output: exports a short summary table with sums of activity units as a regional total 
      and within the buffer
    """

    try:

        fgtswa = utils.get_onedrive_layer(config, 'fgtswa_path', 'FGTSWA')
        activity_units_2050 = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')
        combined_gdf = buffer_and_combine(fgtswa, activity_units_2050)

        total_au = activity_units_2050.sum_au_205.sum()
        summed = sum_combined(combined_gdf, config)
        df = pd.DataFrame({
            'selection': ['regional total', 'within 500 ft of FGTS routes'],
            'activity units': [total_au, summed]
        })
        utils.export_csv(df, config, 'density_and_freight.csv')
        print(f"Finished Density and Freight export")
        
    except Exception as e:
        print(f"Error in run: {e}")
        raise
