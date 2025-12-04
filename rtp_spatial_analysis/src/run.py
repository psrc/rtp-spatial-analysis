import configuration
import yaml
from pathlib import Path
import demo
import density_and_freight
import density_and_signals
import frequent_transit_routes_and_signal
import transit_stop_intersections
import getpass
import paratransit_bnd
import congestion_measures
import rcp_equity_analysis

file = Path().joinpath(configuration.args.configs_dir, "config.yaml")

config = yaml.safe_load(open(file))


if Path().joinpath("C:/Users/", getpass.getuser(), "PSRC").exists():
    config['user_onedrive'] = Path().joinpath("C:/Users/", getpass.getuser(), "PSRC")
elif Path().joinpath("C:/Users/", getpass.getuser(), "Puget Sound Regional Council").exists():
    config['user_onedrive'] = Path().joinpath("C:/Users/", getpass.getuser(), "Puget Sound Regional Council")
else:   
    print ("OneDrive path not found")

if config['run_demo']:
    demo.run(config)
    
if config['run_density_and_freight']:
    density_and_freight.run(config)

if config['run_density_and_signals']:
    density_and_signals.run(config)

if config['run_frequent_transit_routes_and_signal']:
    frequent_transit_routes_and_signal.run(config)
    
if config['run_transit_stop_intersect_future_density']:
    transit_stop_intersections.run_transit_intesection_future_density(config)
    
if config['run_transit_stop_intersect_efa']:
    transit_stop_intersections.run_transit_intesection_efa(config)

if config['run_paratransit_boundary']:
    paratransit_bnd.run(config)    

if config['run_congestion_measures']:
    congestion_measures.run(config)  
     
if config['run_rcp_equity_analysis']:
    rcp_equity_analysis.run(config)