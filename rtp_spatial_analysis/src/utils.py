import geopandas as gpd
import psrcelmerpy
from pathlib import Path 

def buffer_layer(layer_gdf, distance):
    """
    Create a buffered copy of a GeoDataFrame's geometries.

    Applies a buffer operation to all geometries in the input GeoDataFrame,
    expanding or contracting them by the specified distance.

    Args:
        layer_gdf (geopandas.GeoDataFrame): The input GeoDataFrame containing
            geometries to buffer.
        distance (float): The buffer distance in the units of the GeoDataFrame's
            coordinate reference system. Positive values expand geometries,
            negative values contract them.

    Returns:
        geopandas.GeoDataFrame: A copy of the input GeoDataFrame with buffered
            geometries. Returns unchanged copy if distance is 0 or negative.

    Raises:
        Exception: If an error occurs during the buffer operation.
    """
    try:
        if distance > 0:
            buffered_gdf = layer_gdf.copy()
            buffered_gdf.geometry = buffered_gdf.geometry.buffer(distance)
        return buffered_gdf

    except Exception as e:
        print(f"Error in get_buffer_layer: {e}")
        raise

def intersect_layers(df1, df2, how='intersection'):
    """
    Perform a spatial overlay operation between two GeoDataFrames.

    Combines two GeoDataFrames using a specified overlay method, allowing
    for various spatial operations such as intersection, union, or difference.

    Args:
        df1 (geopandas.GeoDataFrame): The first GeoDataFrame for the overlay.
        df2 (geopandas.GeoDataFrame): The second GeoDataFrame for the overlay.
        how (str, optional): The type of overlay operation to perform.
            Options include 'intersection', 'union', 'identity',
            'symmetric_difference', and 'difference'. Defaults to 'intersection'.

    Returns:
        geopandas.GeoDataFrame: A new GeoDataFrame containing the result of
            the overlay operation.
    """
    return df1.overlay(df2, how= how)

def points_in_polygon(points_gdf, polygons_gdf, col_name, buffer=0):
    """
    Check if points intersect polygons and add a boolean column to the result.

    Determines whether each point in the points GeoDataFrame intersects with
    any polygon in the polygons GeoDataFrame. Optionally applies a buffer to
    the points before checking intersection.

    Args:
        points_gdf (geopandas.GeoDataFrame): A GeoDataFrame containing point
            geometries to check for intersection.
        polygons_gdf (geopandas.GeoDataFrame): A GeoDataFrame containing polygon
            geometries to check against.
        col_name (str): The name of the boolean column to add to the points
            GeoDataFrame indicating intersection status.
        buffer (float, optional): Buffer distance to apply to points before
            checking intersection, in the units of the coordinate reference
            system. Defaults to 0 (no buffer).

    Returns:
        geopandas.GeoDataFrame: The input points GeoDataFrame with an additional
            boolean column indicating whether each point intersects the polygons.

    Raises:
        Exception: If an error occurs during the intersection check.
    """
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
    """
    Export a GeoDataFrame to an OpenFileGDB geodatabase.

    Writes the input GeoDataFrame as a layer to an Esri OpenFileGDB geodatabase
    at a location specified in the configuration dictionary.

    Args:
        gdf (geopandas.GeoDataFrame): The GeoDataFrame to export.
        config (dict): Configuration dictionary containing output path settings.
            Must include 'user_onedrive', 'rtp_output_path', and
            'rtp_output_gdb_name' keys.
        lyr_nm (str): The name to assign to the layer in the geodatabase.

    Raises:
        Exception: If an error occurs during the export operation.
    """
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
    """
    Export a DataFrame to a CSV file at a pre-defined location.

    Writes the input DataFrame to a CSV file at a location specified in the
    configuration dictionary.

    Args:
        df (pandas.DataFrame): The DataFrame to export.
        config (dict): Configuration dictionary containing output path settings.
            Must include 'user_onedrive' and 'rtp_output_path' keys.
        file_nm (str): The name of the output CSV file (including .csv extension).
        index (bool, optional): Whether to include the DataFrame index in the
            output file. Defaults to False.

    Raises:
        Exception: If an error occurs during the export operation.
    """
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
