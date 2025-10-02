import geopandas as gpd
import psrcelmerpy
from pathlib import Path 



def buffer_layer(layer_gdf, distance):

    try:
        if distance > 0:
            buffered_gdf = layer_gdf.copy()
            buffered_gdf.geometry = buffered_gdf.geometry.buffer(distance)
        return buffered_gdf

    except Exception as e:
        print(f"Error in get_buffer_layer: {e}")
        raise

def intersect_layers(df1, df2, how='intersection'):
    return df1.overlay(df2, how= how)

def points_in_polygon(points_gdf, polygons_gdf, col_name, buffer=0):
    """Check if a point intersects a polygon with an optional buffer, and add a boolean column."""

    try: 
        if buffer > 0:
            buffered_points_gdf = points_gdf.copy()
            buffered_points_gdf.geometry = buffered_points_gdf.geometry.buffer(buffer)
            intersects = buffered_points_gdf.geometry.intersects(polygons_gdf.geometry.unary_union)
        else:
            intersects = points_gdf.geometry.intersects(polygons_gdf.geometry.unary_union)
        points_gdf[col_name] = intersects
        return points_gdf

    except Exception as e:
        print(f"Error in points_in_polygon: {e}")
        raise

def export_layer(gdf, config, lyr_nm):
    """export to a pre-defined file location"""
    
    try: 
        user_od = config['user_onedrive']
        output_path = config['rtp_output_path']
        gdb_name = config['rtp_output_gdb_name']
        path_to_output = f"{user_od}/{output_path}/{gdb_name}"
        gdf.to_file(path_to_output, layer=lyr_nm, driver="OpenFileGDB")

    except Exception as e:
        print(f"Error in export_layer: {e}")
        raise


def export_csv(df, config, file_nm, index=False):
    """export to a pre-defined file location"""

    try: 
        user_od = config['user_onedrive']
        output_path = config['rtp_output_path']
        path_to_output = f"{user_od}/{output_path}"
        pth = Path(path_to_output,file_nm)
        df.to_csv(pth, index=index)

    except Exception as e:
        print(f"Error in export_csv: {e}")
        raise

def get_onedrive_layer(config, path_name, layer):
    """
    Load a specific layer from a geodatabase file stored in OneDrive.
    
    This function constructs a file path using configuration settings to locate 
    and load a geodatabase layer from OneDrive storage. The loaded data is 
    automatically reprojected to EPSG:2286 (Washington State Plane North).
    
    Args:
        config (dict): Configuration dictionary containing OneDrive path information.
                      Must include 'user_onedrive' key and the key specified by path_name.
        path_name (str): Key name in the config dictionary that contains the relative 
                        path to the geodatabase file from the OneDrive root.
        layer (str): Name of the specific layer to read from the geodatabase file.
    
    Returns:
        geopandas.GeoDataFrame: The loaded spatial layer with CRS transformed to 
                               EPSG:2286 (Washington State Plane North).
    
    """
    try:
        crs = config['epsg_crs']
        f_path = f"{config['user_onedrive']}/{config[path_name]}"
        gdb = gpd.read_file(Path(f_path), layer=layer)
        gdb = gdb.to_crs(crs)
        return(gdb)
    except Exception as e:
        print(f"Error in get_onedrive_layer: {e}")
        raise
