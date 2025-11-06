from pathlib import Path
import geopandas as gpd
import pandas as pd
import utils

# Heavy or Severe Congestion and FGTS routes
  
# Frequent Transit Routes and Heavy or Severe Congestion

def congested_transit_segments(congested_links, transit_segments, transit_routes):   
    congested_transit_segments=transit_segments[transit_segments['ij'].isin(congested_links['ij'])]
    congested_transit_lines=congested_transit_segments.line_id.unique().tolist()
    congested_transit_routes=transit_routes[transit_routes['ID'].isin(congested_transit_lines)]
    return congested_transit_routes


def run(config):
    model_links = pd.read_csv(Path(config['2050_model_run_path'])/"outputs/network/network_results.csv")
    model_links_gdf = gpd.read_file(Path(config['2050_model_run_path'])/"outputs/network/shapefile/emme_links.shp")    
    #model_links["ij"] = model_links["i_node"].astype(str) + "-" + model_links["j_node"].astype(str)
    congested_links = model_links[model_links['congestion_category'].isin(['Heavy', 'Severe'])]
    congested_model_links_gdf = model_links_gdf[model_links_gdf['ID'].isin(congested_links['ij'])]
    congested_fgts = congested_links[congested_links['@fgts'] > 0]
    congested_fgts = model_links_gdf[model_links_gdf['ID'].isin(congested_fgts['ij'])]
    utils.export_layer(congested_fgts, config, "congested_fgts")

    model_transit_segments = pd.read_csv(Path(config['2050_model_run_path'])/"outputs/transit/transit_segment_results.csv", dtype={'i_node': 'Int64', 'j_node': 'Int64'})
    model_transit_segments["i_node"].fillna(0).astype(int)
    model_transit_segments["j_node"].fillna(0).astype(int)
    model_transit_segments["ij"] = model_transit_segments["i_node"].astype(str) + "-" + model_transit_segments["j_node"].astype(str)
    
    model_transit_routes = gpd.read_file(Path(config['2050_model_run_path'])/"outputs/network/shapefile/emme_tlines.shp")
    congested_transit_routes = congested_transit_segments(congested_links, model_transit_segments, model_transit_routes) 
    utils.export_layer(congested_model_links_gdf, config, "congested_links")
  
    signals_gdf = gpd.read_file(Path(f"{config['user_onedrive']}/{config['rtp_its_signals_path']}/ITS_Signals_2024_Final.gdb"), layer="its_signals")
    signals_gdf = signals_gdf.to_crs(2285)
    signals_gdf.geometry = signals_gdf.geometry.buffer(20)  # buffer 100 feet to ensure intersection   
    print(signals_gdf)
    print("signals done")

    signals_in_congested_links_gdf = gpd.sjoin(
        signals_gdf,
        congested_model_links_gdf,
        how="inner",
        predicate="intersects"      
    )
    signals_in_congested_links_gdf=signals_in_congested_links_gdf.drop_duplicates(subset='OBJECTID')
    
    utils.export_layer(signals_in_congested_links_gdf, config, "congested_signals")
       
    print('done')

