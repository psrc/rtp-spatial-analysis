import pandas as pd
import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils


def buffer_and_combine(line_layer, hex_layer):
    """buffer a polyline layer and intersect it with hex_layer"""

    try:
        buffered_gdf = utils.buffer_layer(line_layer, 500)
        intersected = utils.intersect_layers(buffered_gdf, hex_layer)
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


def sum_combined(gdf, au_col_name, config):
    """
    Get a sum of activity units in a geodataframe
    
    Args:
        A gdf with columns "geometry" and "au_acre" (activity units per acre) 

    Returns: 
        An integer representing the summed activity units in the gdf
    """
    try:
        c = gdf[['GRID_ID', 
                au_col_name, 
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
        fgtswa = fgtswa[fgtswa['FGTSClass'].isin(['T-1', 'T-2'])]
        #activity_units_2050 = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')

        au2050 = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')
        combined_gdf = buffer_and_combine(fgtswa, au2050)
        total_au_2050 = au2050.sum_au_205.sum()
        summed_2050 = sum_combined(combined_gdf, 'sum_au_205', config)

        au2024 = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2024')
        combined_gdf = buffer_and_combine(fgtswa, au2024)
        total_au_2024 = au2024.sum_au_202.sum()
        summed_2024 = sum_combined(combined_gdf, 'sum_au_202', config)
        
        df = pd.DataFrame({
            'selection': ['regional total', 'within 500 ft of FGTS routes'],
            'activity units 2050': [total_au_2050, summed_2050],
            'activity units 2024': [total_au_2024, summed_2024],
        })
        utils.export_csv(df, config, 'density_and_freight.csv')
        print(f"Finished Density and Freight export")
        
    except Exception as e:
        print(f"Error in run: {e}")
        raise
