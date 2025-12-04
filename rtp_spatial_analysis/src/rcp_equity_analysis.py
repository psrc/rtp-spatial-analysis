import geopandas as gpd
import pandas as pd
import psrcelmerpy
from pathlib import Path 
import utils
import fiona

def run(config):
    # GET BUFFERED RCP PROJECTS #
    buffered_rcp = get_buffered_rcp(config)
    # print(buffered_rcp)
  
    # # Load tract layer from ElmerGeo
    tract_columns = ["geoid20", "tractce20", "geometry"]
    eg_conn = psrcelmerpy.ElmerGeoConn()
    tract = eg_conn.read_geolayer('TRACT2020', schema_name="dbo", project_to_wgs84= False)
    tract = tract[tract_columns]
    # print(tract)

    # GET EFA TRACTS #
    efa = pd.read_csv(config['user_onedrive']/ config['rtp_efa_path']/ "equity_focus_areas_2023.csv")
    tract['geoid20'] = efa['GEOID20'].astype(str)

    gdf_efa_tract = efa.join(tract, how="left")

    gdf = gpd.clip(gdf_efa_tract, buffered_rcp)
    print(gdf)
    # efa_tract = gdf_efa_tract.drop(columns=['geometry'])


    # print(efa_tract)

    # efa_tracts = open_layer(config, 'rtp_efa_path', 'equity_focus_areas_2023_acs.gdb', 'disabled_vs_mean')
    # efa_tracts = efa_tracts.to_crs(2285)
    # print(efa_tracts)

    # rcp_efa = combine_rcp_efa(buffered_rcp, efa_tracts, config)
    # print(rcp_efa)
    # print("RCP equity combination done")

def get_buffered_rcp(config):
    # Regional Capacity Projects
    # gdb_path = r"C:/Users/ONg/PSRC/GIS - Sharing/Projects/Transportation/RTP_2026/regional_capacity_projects/rtp_projects_2026_scenario_2b/rtp_projects_2026_2b.gdb"
    # layer_name = fiona.listlayers(gdb_path)[0]  # first layer
    # print("Using layer:", layer_name)

    regional_capacity_projs = open_layer(config, 'rcp_path', 'rtp_projects_2026_2b.gdb', 'rtp_projects_scenario_2b')
    regional_capacity_projs = regional_capacity_projs.to_crs(2285)

    # buffer 100 feet
    regional_capacity_projs.geometry = regional_capacity_projs.geometry.buffer(100)

    return regional_capacity_projs

###########################################################################
# Open Layer Function
# Parameters: config dict, path key in config, gdb file name, layer name
# Function: Opens a specified layer from a geodatabase file
# Returns: geopandas dataframe
############################################################################          
def open_layer(config, path, gdb_path, layer):
    path = f"{config['user_onedrive']}/{config[path]}"
    layer_output = gpd.read_file(
        Path(path) / gdb_path,
        layer=layer,
        engine="fiona",
    )
    return layer_output

#############################################################################
# Combine Frequent Transit Routes and Signals Function
# Parameters: transit routes dataframe, signals dataframe, config dict  
# Function: Spatially joins signals with frequent transit routes and exports results
#           to shapefile and CSV
# Returns: geopandas dataframe of signals on frequent transit routes
###############################################################################
def combine_rcp_efa(buffered_rcp, efa_tracts, config):
    # efa = pd.read_csv(config['user_onedrive']/ config['rtp_efa_path']/ "equity_focus_areas_2023.csv")
    # efa['geoid20'] = efa['GEOID20'].astype(str)
    rcp_efa = gpd.sjoin(
        buffered_rcp, efa_tracts, how="inner", predicate="intersects"
    )
    # rcp_efa = rcp_efa.drop_duplicates(subset=buffered_rcp.columns)

    # utils.export_layer(
    #     rcp_efa, config, "rcp_efa.shp"
    # )
    utils.export_csv(
        rcp_efa, config, "rcp_efa.csv"
    )
    return rcp_efa