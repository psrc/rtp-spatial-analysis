import geopandas as gpd
import pandas as pd
import psrcelmerpy
from pathlib import Path 
import utils

transit_supportive_density = {'local':7,
                              'all_day':15,
                              'frequent':25,
                              'hct':40,
                              'brt':15}

# list_efa = ['equity_focus_areas_2023__efa_poc',
#             'equity_focus_areas_2023__efa_pov200',
#             'equity_focus_areas_2023__efa_lep',
#             'equity_focus_areas_2023__efa_youth',
#             'equity_focus_areas_2023__efa_older',
#             'equity_focus_areas_2023__efa_dis']

def export_csv(df, config, file_nm):
    """export to a pre-defined file location"""
    path_to_output = f"{config['user_onedrive']}/{config['rtp_output_path']}"
    pth = Path(path_to_output,file_nm)
    df.to_csv(pth)

def get_service_au(config, buffered_stops, col_suffix):

    gdf = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')
    gdf = gdf.to_crs(2285)

    sum_fields = ['sum_pop_20', 'sum_jobs_2', 'sum_au_205']
    data = {}

    for key, density in transit_supportive_density.items():

        # number of people and jobs that are in supportive densities
        gdf_au = gdf[gdf['au_acre']>=density]
        total_au = gdf_au[sum_fields].sum().to_list()

        transit_by_type = buffered_stops[buffered_stops[key]>0]
        gdf = gpd.clip(gdf_au, transit_by_type)

        _list = gdf[sum_fields].sum().to_list()
        _list_without = [total_au[i] - _list[i] for i in range(len(_list))]
        data[key + col_suffix] = _list +_list_without
    
    df = pd.DataFrame.from_dict(data, orient='index', columns=['people with service', 'jobs with service', 'activity units with service',
                                                               'people w/o service', 'jobs w/o service', 'activity units w/o service'])
    df = df.rename_axis('Route Type')

    return df

def run(config):

    # 2050 Transit Stops
    transit_stops_2050 = utils.get_onedrive_layer(config, 'rtp_transit_network_path', 'Transit_Stops_2050')
    transit_stops_2050 = transit_stops_2050.to_crs(2285)
    
    # buffer 1/4 and 1/2 mile
    buf2_transit_stops_2050 = utils.buffer_layer(transit_stops_2050, config['mile_in_ft']/2)
    buf4_transit_stops_2050 = utils.buffer_layer(transit_stops_2050, config['mile_in_ft']/4)

    # 1. Intersection of transit stops and future density ----
    # get number of people and jobs that are in supportive densities with service and in those in supportive densities without service (Gap)
    test = get_service_au(config, buf2_transit_stops_2050, '_half_mi')
    test2 = get_service_au(config, buf4_transit_stops_2050, '_quarter_mi')
    df_service_dense = pd.concat([test, test2])

    export_csv(df_service_dense, config, "transit_stops_density_intersect.csv")

    # 2. Intersection of transit stops and Equity Focus Areas ----
    # Load blocks layer from ElmerGeo
    # eg_conn = psrcelmerpy.ElmerGeoConn()
    # blocks = eg_conn.read_geolayer("block2020_nowater")
    # blocks = blocks.to_crs(2285) 

    # # get list of all layers in file: gpd.list_layers(Path(user_path)/config['rtp_efa_path'])
    # # 2023 Equity Focused Areas
    # efa_2023 = utils.get_onedrive_layer(config, 'rtp_efa_path', 'overall')
    # efa_2023 = pd.DataFrame(efa_2023.drop(columns=['Shape_Length', 'Shape_Area', 'geometry']))
    # efa_2023.loc[:,'tractce20'] =  efa_2023['L0ElmerGeo_DBO_tract2020_nowater_geoid20'].str[-6:]

    # # get block-level population with EFA assignments
    # block_efa_2023 = blocks[['geoid20', 'county_name', 'tractce20', 'total_pop20', 'geometry']].\
    #     merge(efa_2023, on='tractce20')
    # block_efa_2023['total_pop20'] = block_efa_2023['total_pop20'].astype('float')




    
    
    # local_transit = buf_half_transit_stops_2050[buf_half_transit_stops_2050['local']>0]
    # block_efa_poc = block_efa_2023[block_efa_2023['equity_focus_areas_2023__efa_poc']>0]

    # gdf = gpd.clip(block_efa_poc, local_transit)
    # df = pd.DataFrame(gdf.drop(columns='geometry'))

    # efa_poc_block = utils.intersect_layers(blocks, equity_focus_areas_2023__efa_poc)
    
    # plt = combined_gdf.plot(figsize=(10, 6))
    # plt.savefig('world_map.png')

    # transit_stops_2050 = points_in_polygon(transit_stops_2050, blocks, "in_city_100ft", buffer=100)
    print ('done')




