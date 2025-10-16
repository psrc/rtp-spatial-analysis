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

def cal_service_area_stat(df_total, df_within, pct_col_names):
    """
    get population or activity units within service area, outside service area, and percentage
    """

    df_outside = df_total - df_within
    # percentage
    within_percent = df_within/df_total
    within_percent.columns = pct_col_names
    outside_percent = df_outside/df_total
    outside_percent.columns = pct_col_names
    ## total percent should all be 1
    total_percent = df_total/df_total
    total_percent.columns = pct_col_names

    within_all = pd.concat([df_within, within_percent], axis=1)
    within_all['Area'] = "Inside Buffered TRS"
    outside_all = pd.concat([df_outside, outside_percent], axis=1)
    outside_all['Area'] = "Outside Buffered TRS"
    total_all = pd.concat([df_total, total_percent], axis=1)
    total_all['Area'] = "Total"

    df = pd.concat([within_all, outside_all, total_all])
    
    # formatting
    df[df_within.columns] = df[df_within.columns].round(1)
    df[pct_col_names] = df[pct_col_names].map(lambda x: f'{x:.1%}')

    return df

def result_au_service(config, buffered_stops, buffer_name):

    gdf = utils.get_onedrive_layer(config, 'activity_units_path', 'peope_and_jobs_2050')
    gdf = gdf.to_crs(2285)

    sum_fields = ['sum_pop_20', 'sum_jobs_2', 'sum_au_205']
    total_col = ['population', 'jobs', 'activity_units'] 
    pct_cols = [i + '_pct' for i in total_col]
    data = {}

    for key, density in transit_supportive_density.items():

        # number of people and jobs that are in supportive densities
        gdf_au = gdf[gdf['au_acre']>=density]
        total_au = gdf_au.groupby('county', observed=False)[sum_fields].sum()
        total_au.columns = total_col

        transit_by_type = buffered_stops[buffered_stops[key]>0]
        # gdf = gpd.clip(gdf_au, transit_by_type)
        gdf = gpd.clip(gdf_au, transit_by_type)
        df = gdf.drop(columns=['geometry'])

        within = df.groupby('county', observed=False)[sum_fields].sum().fillna(0)
        within.columns = total_col
        # get activity units inside, outside, and total with percentage
        data[key] = cal_service_area_stat(total_au, within, pct_cols)
    
    # create final dataframe from data dictionary
    df = pd.concat(data.values(),
                   keys=data.keys(),
                   names=['Route Type']).reset_index()
    df['Buffer'] = buffer_name
    df = df[['county', 'Route Type', 'Buffer', 'Area'] + total_col + pct_cols].copy()

    return df


def get_parcel_with_efa_pop(config):
    # read population from parcel
    parcel_columns = ["parcel_id", "population_2050", "geometry"]
    gdf_parcel = utils.get_onedrive_layer(config, 'au_path', 'draft_parcel_data_rtp_2026')
    # only keep parcels with population
    gdf_parcel = gdf_parcel[gdf_parcel['population_2050']>0]
    gdf_parcel = gdf_parcel[["parcel_id", "population_2050", "geometry"]]
    
    # Load tract layer from ElmerGeo
    tract_columns = ["geoid20", "county_name", "tractce20", "geometry"]
    eg_conn = psrcelmerpy.ElmerGeoConn()
    tract = eg_conn.read_geolayer('TRACT2020', project_to_wgs84= False)
    tract = tract[tract_columns]

    # get list of all layers in file: gpd.list_layers(Path(user_path)/config['rtp_efa_path'])
    # 2023 Equity Focused Areas
    efa = pd.read_csv(config['user_onedrive']/ config['rtp_efa_path']/ "equity_focus_areas_2023.csv")
    efa['geoid20'] = efa['GEOID20'].astype(str)
    # filter columns: keep population percentage by efa type
    efa_pct_cols = efa.columns[efa.columns.str.endswith('prct_est')]
    efa_pop_cols = efa_pct_cols.str.replace('_prct_est', '_efa_pop', regex=False)
    efa = efa[['geoid20'] + efa_pct_cols.tolist()].fillna(0).copy()
    
    # spatial join parcel with tract to get geoid
    gdf_parcel_tract = gdf_parcel.sjoin(tract, how="left")
    parcel_tract = gdf_parcel_tract.drop(columns=['geometry'])

    # merge parcel_tract with efa: get percentage of population
    parcel_tract_efa = parcel_tract.merge(efa, on='geoid20', how='inner')
    # estimate population in each efa by multiplying percentage with total population in each parcel
    parcel_tract_efa[efa_pop_cols] = parcel_tract_efa[efa_pct_cols].mul(parcel_tract_efa['population_2050'], axis=0)
    parcel_tract_efa = parcel_tract_efa[['parcel_id', 'geoid20', 'county_name'] + efa_pop_cols.to_list()].copy()
    # create catgorical type for county_name to keep all counties in the output table
    parcel_tract_efa['county_name'] = parcel_tract_efa['county_name'].astype('category')
    
    # merge back with parcel to get geometry
    gdf_parcel_efa = gdf_parcel.merge(parcel_tract_efa, on='parcel_id', how='inner')

    return(gdf_parcel_efa)


def result_efa_pop_service(parcel, buffered_stops, buffer_name):

    # list of efa column names
    efa_pop_cols = parcel.columns[parcel.columns.str.endswith('efa_pop')]
    # pop_cols = efa_pop_cols.str.replace('_efa_pop', '_pop', regex=False).to_list()
    pct_cols = efa_pop_cols.str.replace('_efa_pop', '_pct', regex=False).to_list()
    # total population in each efa
    efa_total_pop = parcel.groupby('county_name', observed=False)[efa_pop_cols].sum()
    
    # dictionary to hold dataframes for each transit type
    data = {}
    # [loop through transit types] get population in each efa with service, without service, and total
    for key in transit_supportive_density.keys():
        
        # get buffered stops by transit type
        transit_by_type = buffered_stops[buffered_stops[key]>0]
        gdf = gpd.clip(parcel, transit_by_type)
        
        df = gdf.drop(columns=['geometry'])
        # total population in each efa with/without service
        within = df.groupby('county_name', observed=False)[efa_pop_cols].sum().fillna(0)
        # get population inside, outside, and total with percentage
        data[key] = cal_service_area_stat(efa_total_pop, within, pct_cols)

    # create final dataframe from data dictionary
    df = pd.concat(data.values(),
                   keys=data.keys(),
                   names=['Route Type']).reset_index()
    df['Buffer'] = buffer_name
    df = df[['county_name', 'Route Type', 'Buffer', 'Area'] + efa_pop_cols.tolist() + pct_cols].copy()

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
    df1 = result_au_service(config, buf2_transit_stops_2050, 'half mile')
    df2 = result_au_service(config, buf4_transit_stops_2050, 'quarter mile')
    df_service_dense = pd.concat([df1, df2])

    # save to output folder
    utils.export_csv(df_service_dense, config, "transit_stops_density_intersect.csv")

    # 2. Intersection of transit stops and Equity Focus Areas ----
    gdf_parcel_efa = get_parcel_with_efa_pop(config)
        
    df1 = result_efa_pop_service(gdf_parcel_efa, buf2_transit_stops_2050, 'half mile')
    df2 = result_efa_pop_service(gdf_parcel_efa, buf4_transit_stops_2050, 'quarter mile')
    df_pop_service = pd.concat([df1, df2])

    # save to output folder
    utils.export_csv(df_pop_service, config, "transit_stops_efa_pop_intersect.csv")
    
    print ('done')




