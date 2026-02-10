from . import utils
import os
import pandas as pd
import geopandas as gpd
import psrcelmerpy
from pathlib import Path 

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.9f' % x)

def buffer_transit_routes(config):
    """
    Remove Sounder, ST Express, and Ferries from transit routes:
        Sounder -> route_type==2 and agency==6.
        ST Express -> route_type==3 and agency ==6.
        Ferries -> route_type == 4.    

    """
    print('Read transit routes')
    trs = utils.get_onedrive_layer(config, 'rtp_transit_network_path', 'transit_routes_2050')
    trs_filtered = trs[~((trs['route_type'].isin([2, 3])) & (trs['agency_id'] == "6") | (trs['route_type'] == 4))]
 
    # buffer transit routes
    trs_buff = utils.buffer_layer(layer_gdf = trs_filtered, distance = config['mile_in_ft']*.75)
    trs_buff = trs_buff[['route_id', 'geometry']]
    trs_buff = trs_buff.dissolve()
    trs_buff.loc[trs_buff['route_id'].notna(), 'route_id'] = 'Inside Buffered TRS'
    return(trs_buff)

def create_parcel_overlay(config):
    """
    Overlay of parcelized activity units, tracts, and buffered transit routes. 

    Remove Sounder, ST Express, and Ferries from transit routes:
        Sounder -> route_type==2 and agency==6.
        ST Express -> route_type==3 and agency ==6.
        Ferries -> route_type == 4.    

    """

    trs_buff = buffer_transit_routes(config)

    # read activity units layer
    print('Read AU')
    au_columns = ['population_2050', "geometry"]
    au = utils.get_onedrive_layer(config, 'au_path', 'draft_parcel_data_rtp_2026')
    au = au[au_columns]

    # overlay with CT 2020
    tract_columns = ["population_2050", "geoid20", "countyfp", "county_name", "tractce20", "geometry"]
    eg_conn = psrcelmerpy.ElmerGeoConn()
    tract = eg_conn.read_geolayer('TRACT2020')
    tract = tract.to_crs(2285)
    au_tract = gpd.sjoin(au, tract, how="left")
    au_tract = au_tract[tract_columns]

    # overlay with buffered transit routes
    au_tract_trs = gpd.sjoin(au_tract, trs_buff, how="left")

    # clean up au_tract_trs, one parcel missing tract information
    au_tract_trs['route_id'] = au_tract_trs['route_id'].fillna("Outside Buffered TRS")
    missing_tract = au_tract_trs[au_tract_trs['countyfp'].isnull() & au_tract_trs['population_2050'] > 0]
    missing_tract = missing_tract.drop(['index_right'], axis=1)
    missing_tract_join = gpd.sjoin_nearest(missing_tract, tract[['countyfp', 'geoid20', 'geometry']], how="left")
    missing_tract_join = missing_tract_join[['countyfp_right', 'geoid20_right']]
    missing_tract_join.rename(columns={'countyfp_right': 'countyfp', 'geoid20_right':'geoid20'}, inplace=True)

    au_tract_trs.update(missing_tract_join) # update missing info from missing tract table

    return(au_tract_trs)


def create_denom(overlay_tbl):
    """
    Tablulate total regional and county population 2050 into dataframe.

    Args:
     The overlay_tbl: a shape of the overlay of parcelized activity units, tracts, and buffered transit routes.    

    """

    reg = overlay_tbl['population_2050'].sum()
    cnty = overlay_tbl.groupby(['countyfp'])['population_2050'].sum().reset_index()
    denom = pd.concat([cnty, pd.DataFrame([{'countyfp': 'Region', 'population_2050': reg}])], ignore_index=True) 
    denom.rename(columns={'population_2050':'denom_pop50'}, inplace=True)
    return(denom)

def run(config):
    """
    For more info on EFA layers:
        https://www.arcgis.com/sharing/rest/content/items/89fb6e03dbd149b8a3e468d85e74e153/info/metadata/metadata.xml?format=default&output=html (metadata)

    """
    au_tract_trs = create_parcel_overlay(config)

    # group by tract, county, buffer and sum
    tract_pop = au_tract_trs.groupby(['geoid20', 'countyfp', 'route_id'])['population_2050'].sum().reset_index()

    # read table with all EFA columns
    print('reading EFA table')
    efa_tbl = r"GIS - Sharing\Projects\Transportation\RTP_2026\equity_focus_areas\efa_3groupings_1SD"
    efa = pd.read_csv(os.path.join(config['user_onedrive'], efa_tbl, "equity_focus_areas_2023.csv"))
    efa['geoid20'] = efa['GEOID20'].astype(str)
    
    # join EFA table to main tract summary
    print("join table to tract summary")
    tract_pop_efa = pd.merge(left = tract_pop, right = efa, on='geoid20', how='left')

    print("compile table")

    # create table with denominators
    denom_pop = create_denom(overlay_tbl = au_tract_trs)

    # multiply population 2050 by percent value for each equity category
    pct_eft_cols = tract_pop_efa.columns[tract_pop_efa.columns.str.endswith('prct_est')]
    res_cols = [col + "_pop50" for col in pct_eft_cols] # columns with results
    res_cols = [col.replace('_prct_est_', '_') for col in res_cols]

    tract_pop_efa[res_cols] = tract_pop_efa[pct_eft_cols].multiply(tract_pop_efa['population_2050'], axis=0) 

    # # export this file for % source if necessary
    # tract_pop_efa_out_cols = ['geoid20', 'countyfp', 'route_id', *pct_eft_cols, *res_cols] 
    # tract_pop_efa_out = tract_pop_efa[tract_pop_efa_out_cols]
    
    # create main summary table by county and region
    main_cols = ['geoid20', 'countyfp', 'route_id', *res_cols]
    df = tract_pop_efa[main_cols]
    df = df.fillna(0)
    
    # merge county and regional summaries
    cnty_sum = df.groupby(['countyfp', 'route_id'])[res_cols].sum().reset_index()
    reg_sum = df.groupby(['route_id'])[res_cols].sum().reset_index()
    reg_sum['countyfp'] = 'Region'
    df_res = pd.concat([cnty_sum, reg_sum], ignore_index=True)

    # sum by juris totals & concatentate
    est_cols = df_res.columns[df_res.columns.str.endswith('pop50')]

    df_res_juris = df_res.groupby(['countyfp']).sum([est_cols]).reset_index()
    df_res_juris['route_id'] = "Total"
    df_res = pd.concat([df_res, df_res_juris], ignore_index=True)
    df_res = df_res.sort_values(by=['countyfp', 'route_id'])
    df_total = pd.merge(df_res, denom_pop, on='countyfp')
    
    # calculate shares
    share_res_cols = [col + "_share" for col in res_cols]
    df_total[share_res_cols] = df_total[res_cols].div(df_total['denom_pop50'], axis=0)
    df_total = df_total.rename(columns={'countyfp':'jurisdiction', 'route_id':'area'})

    # format
    df_total[est_cols] = df_total[est_cols].round(1)
    df_total[share_res_cols] = df_total[share_res_cols].applymap(lambda x: f'{x:.1%}')

    # create file geodatabase for route buffered
    print('export buffered transit routes to gdb')
    trs_buff = buffer_transit_routes(config)
    utils.export_layer(gdf = trs_buff, config = config, lyr_nm = "paratransit_routes_buff.shp")
    # trs_buff.to_file(r"C:\Users\CLam\github\rtp-spatial-analysis\test-shp\trs_buff.shp")

    # export table (csv) of population in Paratransit boundary
    utils.export_csv(df_total, config, "population-in-paratransit-boundaries.csv", index=True)
    print('Complete')