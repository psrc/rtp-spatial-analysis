import geopandas as gpd
import psrcelmerpy
from pathlib import Path 


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

def run(config):
    # Load cities layer from ElmerGeo
    eg_conn = psrcelmerpy.ElmerGeoConn()
    cities = eg_conn.read_geolayer("cities")
    cities = cities.to_crs(2285) 

    # 2050 Transit Stops
    transit_path = f"{config['user_onedrive']}/{config['rtp_transit_data_path']}"
    transit_stops_2050 = gpd.read_file(Path(transit_path)/"Transit_Network_2050_Scenario2b.gdb", layer='Transit_Stops_2050')
    transit_stops_2050 = transit_stops_2050.to_crs(2285)
    transit_stops_2050 = points_in_polygon(transit_stops_2050, cities, "in_city_100ft", buffer=100)
    print ('done')




