import geopandas as gpd
import pandas as pd
import psrcelmerpy
from pathlib import Path 
import utils

list_transit_type = ['local', 'all_day', 'frequent', 'hct', 'brt']
list_efa = ['equity_focus_areas_2023__efa_poc',
            'equity_focus_areas_2023__efa_pov200',
            'equity_focus_areas_2023__efa_lep',
            'equity_focus_areas_2023__efa_youth',
            'equity_focus_areas_2023__efa_older',
            'equity_focus_areas_2023__efa_dis']

def export_csv(df, config, file_nm):
    """export to a pre-defined file location"""
    path_to_output = f"{config['user_onedrive']}/{config['rtp_output_path']}"
    pth = Path(path_to_output,file_nm)
    df.to_csv(pth)

def get_service_au(df_au, buffered_stops, col_suffix):

    sum_fields = ['sum_pop_20', 'sum_jobs_2', 'sum_au_205']
    total_au = df_au[sum_fields].sum().to_list()
    data = {}

    for type in list_transit_type:

        transit_by_type = buffered_stops[buffered_stops[type]>0]
        gdf = gpd.clip(df_au, transit_by_type)

        _list = gdf[sum_fields].sum().to_list()
        _list_without = [total_au[i] - _list[i] for i in range(len(_list))]
        data[type + col_suffix] = _list +_list_without
    
    df = pd.DataFrame.from_dict(data, orient='index', columns=['people with service', 'jobs with service', 'activity units with service',
                                                               'people w/o service', 'jobs w/o service', 'activity units w/o service'])
    df = df.rename_axis('Route Type')

    return df

def run(config):

    # 2050 Transit Stops
    transit_stops_2050 = gpd.read_file(Path(config['user_onedrive'])/config['rtp_transit_network_path'], layer='Transit_Stops_2050')
    transit_stops_2050 = transit_stops_2050.to_crs(2285)
    
    # buffer 1/4 and 1/2 mile
    buf2_transit_stops_2050 = utils.buffer_layer(transit_stops_2050, config['mile_in_ft']/2)
    buf4_transit_stops_2050 = utils.buffer_layer(transit_stops_2050, config['mile_in_ft']/4)

    # Intersection of transit stops and future density ----
    activity_units = gpd.read_file(Path(config['user_onedrive'])/config['activity_units_path'], layer='peope_and_jobs_2050')
    activity_units = activity_units.to_crs(2285)
    # number of people and jobs that are in supportive densities
    activity_units_dense = activity_units[activity_units['density']>=30]

    # get number of people and jobs that are in supportive densities with service and in those in supportive densities without service (Gap)
    test = get_service_au(activity_units_dense, buf2_transit_stops_2050, '_half_mi')
    test2 = get_service_au(activity_units_dense, buf4_transit_stops_2050, '_quarter_mi')
    df_service_dense = pd.concat([test, test2])

    export_csv(df_service_dense, config, "transit_stops_density_intersect.csv")

    # Intersection of transit stops and Equity Focus Areas ----

    # Load blocks layer from ElmerGeo
    # eg_conn = psrcelmerpy.ElmerGeoConn()
    # blocks = eg_conn.read_geolayer("block2020_nowater")
    # blocks = blocks.to_crs(2285) 

    # # get list of all layers in file: gpd.list_layers(Path(user_path)/config['rtp_efa_path'])
    # # 2023 Equity Focused Areas
    # df_efa_overall_2023 = gpd.read_file(Path(user_path)/config['rtp_efa_path'], layer='overall')
    # df_efa_overall_2023 = pd.DataFrame(df_efa_overall_2023.drop(columns=['Shape_Length', 'Shape_Area', 'geometry']))
    # df_efa_overall_2023.loc[:,'tractce20'] =  df_efa_overall_2023['L0ElmerGeo_DBO_tract2020_nowater_geoid20'].str[-6:]

    # # get block-level population with EFA assignments
    # block_efa_2023 = blocks[['geoid20', 'county_name', 'tractce20', 'total_pop20', 'geometry']].\
    #     merge(df_efa_overall_2023, on='tractce20')
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




