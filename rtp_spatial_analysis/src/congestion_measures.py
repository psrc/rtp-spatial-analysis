from pathlib import Path
import geopandas as gpd
import pandas as pd
import utils

# Heavy or Severe Congestion and FGTS routes
# Function to identify congested links with fgts > 0 and export to shapefile and gdb

def congested_fgts(congested_links_fgts, network_gdf):
    # select links from network gdf that are in congested links and have @fgts > 0
    congested_links_fgts = network_gdf[network_gdf['ID'].isin(congested_links_fgts['ij'])]
    congested_links_fgts = congested_links_fgts[congested_links_fgts['@fgts'] > 0]
    congested_links_fgts = congested_links_fgts[['ID', '@fgts', 'geometry']]
    congested_links_fgts = congested_links_fgts.sort_values(by='@fgts', ascending=False)
    return congested_links_fgts

   

# Frequent Transit Routes and Heavy or Severe Congestion
#
#def congested_transeg(congested_links, freqtran_gdf):
    # select frequent routes from transit gdf that are in congested links
#    congested_links = network_gdf[network_gdf['ID'].isin(congested_links['ij'])]
#    congested_freqroutes = transit_gdf[transit_gdf['link_id'].isin(congested_links['ij'])]
#    congested_freqroutes = congested_freqroutes[['route_id', 'link_id', 'geometry']]
#    congested_freqroutes = congested_freqroutes.sort_values(by='route_id')
#    congested_freqroutes.to_file("congested_freqtran.shp")

    #export to file gdb
#    congested_freqroutes.to_file("congested_freqtran.gdb", driver="OpenFileGDB")

def run(config):
    model_links = pd.read_csv(Path(config['2050_model_run_path'])/"outputs/network/network_results.csv")
    model_links = model_links[model_links['congestion_category'].isin(['Heavy', 'Severe'])]
    network_gdf = gpd.read_file(Path(config['2050_model_run_path'])/"outputs/network/shapefile/emme_links.shp")
    congested_links=congested_fgts(model_links, network_gdf)
    #congested_links.to_file(Path(f"{config["rtp_output_path"]}/future_system_output.gdb"), layer="congested_fgts", driver="OpenFileGDB")
    utils.export_layer(congested_links, config, "congested_fgts.shp")


 #   congested_transeg(model_links, gpd.read_file(config['frequent_transit_routes_shapefile']))
   
    print('done')

