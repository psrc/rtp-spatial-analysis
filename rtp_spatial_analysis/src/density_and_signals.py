import pandas as pd
import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
import utils


def export_shp(gdf):
    """export to a pre-defined file location"""

    try:
        pth = Path("C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp")
        gdf.to_file(pth)

    except Exception as e:
        print(f"Error in export_shp: {e}")
        raise


def run(config):
    """
    Create a layer of signals with accessible pedestrian signals 
    that are within high-density activity unit hex's (defined as activity units per acre > 25)
    
    Output: A layer in a geodatabase
    """

    try:

        signals = utils.get_onedrive_layer(config, 'its_signals_path', 'its_signals')
        # signals['ped_signal'] = signals['ped_signal'].fillna(0)
        signals['ped_signal'] = signals['ped_signal'].replace('Null', 'No')
        ped_signals = signals.query("ped_signal == 'Yes'")
        au_2050 = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')
        au_2050['is_dense'] = au_2050['au_acre'].apply(lambda x: 'high density' if x > 25 else 'low density')
        gdf_ped_signals_with_density = signals.sjoin(au_2050, how='inner', predicate='within')
        
        gdf = gdf_ped_signals_with_density.drop('OBJECTID', axis=1)
        x_tab = pd.crosstab(gdf['ped_signal'], gdf['is_dense'])
        utils.export_csv(x_tab, config, 'density_and_signals.csv', index=True)
        utils.export_layer(gdf, config, lyr_nm='accesible_ped_signals_in_dense_areas')
        print(f"Finished Density and Signals")
        
    except Exception as e:
        print(f"Error in run: {e}")
        raise
