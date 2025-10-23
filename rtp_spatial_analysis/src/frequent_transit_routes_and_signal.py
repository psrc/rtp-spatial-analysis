import geopandas as gpd
import psrcelmerpy
from pathlib import Path
import utils
import pandas as pd

def run(config):
    # OPENING FREQUENT TRANSIT ROUTES LAYER #
    transit_routes = open_layer(config, 'rtp_transit_data_path', "Transit_Network_2050_Scenario2b.gdb", "transit_routes_2050")
    transit_routes_frequent = transit_routes[transit_routes["frequent"] == 1]
    transit_routes_frequent = transit_routes_frequent.to_crs(2285)

    # print statements for testing #
    transit_routes_frequent = transit_routes_frequent.reset_index(drop=True)
    print(transit_routes_frequent)
    print("transit routes done")

    # OPENING ITS SIGNALS LAYER #
    signals = open_layer(config, 'rtp_its_signals_path', "ITS_Signals_2024_Final.gdb", "ITS_Signals")
    signals = signals.to_crs(2285)
    signals.geometry = signals.geometry.buffer(100)

    # print statements for testing #
    print(signals)
    print("signals done")

    # COMBINING FREQUENT TRANSIT ROUTES AND ITS SIGNALS INTO SHP FILE AND CSV OUTPUT#
    signals_on_routes = combine_frequent_transit_and_signals(transit_routes_frequent, signals, config)
    
    # print statements for testing #
    print(signals_on_routes)
    print("combining done")

    # SUMMARIZING TSP AND PEDESTRIAN SIGNAL COUNTS #
    sum_yes_no(signals_on_routes, "tsp", "tsp_counts.csv", config)
    sum_yes_no(signals_on_routes, "ped_signal", "ped_signal_counts.csv", config)
    

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
def combine_frequent_transit_and_signals(transit_routes_frequent, signals, config):
    signals_on_routes = gpd.sjoin(
        signals, transit_routes_frequent, how="inner", predicate="intersects"
    )
    signals_on_routes = signals_on_routes.drop_duplicates(subset=signals.columns)

    utils.export_layer(
        signals_on_routes, config, "frequent_transit_routes_and_signal.shp"
    )
    utils.export_csv(
        signals_on_routes, config, "frequent_transit_routes_and_signal.csv"
    )
    return signals_on_routes

#############################################################################
# Summarize Yes/No Counts Function
# Parameters: layer dataframe, column name, csv file name, config dict
# Function: Counts 'Yes' and 'No' values in a specified column and exports 
#           results to CSV by calling count_rows function    
# Returns: None
###############################################################################
def sum_yes_no(layer, column, csv_path, config):
    num_yes = (layer[column] == "Yes").sum()
    num_no = (layer[column] == "No").sum()
    count_rows(num_yes, num_no, csv_path, column, config)

    # print statements for testing #
    print(f"Counts for {column}:")
    print("yes:", num_yes)
    print("no:", num_no)

############################################################################
# Count Rows Function
# Parameters: number of yes, number of no, file name, column name, config dict
# Function: Creates a dataframe with counts of 'Yes' and 'No' and exports to CSV
# Returns: None
############################################################################
def count_rows(num_yes, num_no, file_name, column_name, config):
    counts_df = pd.DataFrame({column_name: ["yes", "no"], "count": [num_yes, num_no]})
    utils.export_csv(counts_df, config, file_name)
