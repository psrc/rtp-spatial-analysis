from pathlib import Path
import geopandas as gpd
import pandas as pd

def congested_fgts(congested_links, network_gdf):
    # select links from network gdf that are in congested links and have @fgts > 0
    congested_links = network_gdf[network_gdf['ID'].isin(congested_links['ij'])]
    congested_links = congested_links[congested_links['@fgts'] > 0]
    congested_links = congested_links[['ID', '@fgts', 'geometry']]
    congested_links = congested_links.sort_values(by='@fgts', ascending=False)
    congested_links.to_file("congested_fgts.shp")

    #export to file gdb
    congested_links.to_file("congested_fgts.gdb", driver="OpenFileGDB")
   
def run(config):
    model_links = pd.read_csv(Path(config['2050_model_run_path'])/"outputs/network/network_results.csv")
    model_links = model_links[model_links['congestion_category'].isin(['Heavy', 'Severe'])]
    network_gdf = gpd.read_file(Path(config['2050_model_run_path'])/"outputs/network/shapefile/emme_links.shp")
    congested_fgts(model_links, network_gdf)
   
    print('done')
