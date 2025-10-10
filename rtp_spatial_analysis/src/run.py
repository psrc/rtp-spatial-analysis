import configuration
import yaml
from pathlib import Path
import demo
import density_and_freight
import transit_stop_intersections
import getpass
import congestion_measures

file = Path().joinpath(configuration.args.configs_dir, "config.yaml")

config = yaml.safe_load(open(file))
config['user_onedrive'] = Path().joinpath("C:/Users/", getpass.getuser(), "Puget Sound Regional Council")

if config['run_demo']:
    demo.run(config)
    
if config['run_density_and_freight']:
    density_and_freight.run(config)
    
if config['run_transit_stop_intersections']:
    transit_stop_intersections.run(config)


if config['run_congestion_measures']:
    congestion_measures.run(config)   
