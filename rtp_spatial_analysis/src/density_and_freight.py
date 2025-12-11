"""
Density and Freight Analysis Module
====================================

This module provides functionality for analyzing activity unit density 
within proximity of Freight and Goods Transportation System (FGTS) routes 
in the Regional Transportation Plan.

The analysis involves:

* Buffering FGTS polyline routes (T-1 and T-2 classifications)
* Intersecting the buffered zones with activity unit hex grid layers
* Calculating and summarizing activity units within the buffer zones
* Comparing regional totals against values within freight corridors

Example
-------
To run the full density and freight analysis::

    from rtp_spatial_analysis.src import density_and_freight
    from rtp_spatial_analysis.src.configuration import Config
    
    config = Config().config
    density_and_freight.run(config)

"""

import pandas as pd
import geopandas as gpd
import psrcelmerpy
from pathlib import Path 
from . import configuration
from . import utils


def buffer_and_combine(line_layer, hex_layer):
    """
    Buffer a polyline layer and intersect it with a hex grid layer.
    
    Creates a 500-foot buffer around the input polyline features and 
    performs a spatial intersection with the provided hexagonal grid layer.
    This is commonly used to identify activity units that fall within 
    proximity of transportation routes.
    
    :param line_layer: A GeoDataFrame containing polyline geometry features 
        (e.g., FGTS routes) to be buffered.
    :type line_layer: geopandas.GeoDataFrame
    :param hex_layer: A GeoDataFrame containing hexagonal grid polygons with 
        activity unit data to intersect with the buffer.
    :type hex_layer: geopandas.GeoDataFrame
    
    :returns: A GeoDataFrame containing the intersection of the buffered 
        polylines and the hex grid, preserving attributes from both layers.
    :rtype: geopandas.GeoDataFrame
    
    :raises Exception: If buffering or intersection operations fail due to 
        invalid geometries or other spatial processing errors.
    
    .. seealso::
        :func:`utils.buffer_layer`, :func:`utils.intersect_layers`
    """

    try:
        buffered_gdf = utils.buffer_layer(line_layer, 500)
        intersected = utils.intersect_layers(buffered_gdf, hex_layer)
        return intersected

    except Exception as e:
        print(f"Error in buffer_and_combine: {e}")
        raise

def export_shp(gdf):
    """
    Export a GeoDataFrame to a shapefile at a pre-defined file location.
    
    Writes the provided GeoDataFrame to a hardcoded output path. This function 
    is primarily used for debugging or interim data exports during development.
    
    :param gdf: The GeoDataFrame to export as a shapefile.
    :type gdf: geopandas.GeoDataFrame
    
    :returns: None
    :rtype: None
    
    :raises Exception: If the file export fails due to permission issues, 
        invalid path, or geometry errors.
    
    .. warning::
        This function uses a hardcoded file path 
        (``C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp``).
        Consider using a configurable path for production use.
    """

    try:
        pth = Path("C:/Users/cpeak/temp/rtp_spatial_analysis_exports/out_shape.shp")
        pth = Path(config['rtp_output_path']) / "out_shape.shp"
        gdf.to_file(pth)

    except Exception as e:
        print(f"Error in export_shp: {e}")
        raise


def sum_combined(gdf, au_col_name, config):
    """
    Calculate the sum of activity units in a GeoDataFrame.
    
    Computes the total activity units by:
    
    1. Extracting relevant columns including geometry and activity units per acre
    2. Calculating the acreage of each polygon from its geometry
    3. Multiplying activity units per acre by acreage to get total activity units
    4. Summing all activity units across the GeoDataFrame
    
    :param gdf: A GeoDataFrame containing polygon geometries with activity unit 
        density data. Must include columns for ``GRID_ID``, the activity unit 
        column specified by ``au_col_name``, ``au_acre`` (activity units per acre), 
        and ``geometry``.
    :type gdf: geopandas.GeoDataFrame
    :param au_col_name: The name of the column containing activity unit values 
        (e.g., ``'sum_au_205'`` for 2050 data or ``'sum_au_202'`` for 2024 data).
    :type au_col_name: str
    :param config: Configuration dictionary containing conversion factors. 
        Must include the key ``'acre_in_sqft'`` specifying square feet per acre.
    :type config: dict
    
    :returns: The total sum of activity units across all polygons in the 
        GeoDataFrame.
    :rtype: float
    
    :raises KeyError: If required columns are missing from the GeoDataFrame 
        or if ``'acre_in_sqft'`` is not in the config dictionary.
    :raises Exception: If calculation fails due to invalid data types or 
        other processing errors.
    
    .. note::
        NaN values in ``au_acre`` and ``acreage`` columns are filled with 0 
        before multiplication to prevent null results.
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
    Execute the density and freight analysis workflow.
    
    This is the main entry point for the density and freight analysis. It 
    calculates activity unit density within 500 feet of FGTS (Freight and 
    Goods Transportation System) routes classified as T-1 or T-2.
    
    The workflow performs the following steps:
    
    1. Loads FGTS route data and filters for T-1 and T-2 classifications
    2. Loads activity unit data for both 2050 (projected) and 2024 (current) years
    3. Creates 500-foot buffers around FGTS routes
    4. Intersects buffers with activity unit hex grids
    5. Calculates regional totals and buffer-specific totals
    6. Exports results to a CSV summary table
    
    :param config: Configuration dictionary containing file paths and settings.
        Required keys include:
        
        * ``'fgtswa_path'``: Path to FGTS routes layer
        * ``'activity_units_path'``: Path to activity units data
        * ``'acre_in_sqft'``: Conversion factor for area calculations
        * Output path settings for CSV export
        
    :type config: dict
    
    :returns: None. Results are exported to ``density_and_freight.csv``.
    :rtype: None
    
    :raises FileNotFoundError: If input data files specified in config cannot 
        be found.
    :raises KeyError: If required configuration keys are missing.
    :raises Exception: If spatial processing or data export operations fail.
    
    **Output Format**
    
    The exported CSV contains the following columns:
    
    ==================== ================================================
    Column               Description
    ==================== ================================================
    selection            Either 'regional total' or 'within 500 ft of 
                         FGTS routes'
    activity units 2050  Projected activity units for 2050
    activity units 2024  Current activity units for 2024
    ==================== ================================================
    
    .. seealso::
        :func:`buffer_and_combine`, :func:`sum_combined`, 
        :func:`utils.export_csv`
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
