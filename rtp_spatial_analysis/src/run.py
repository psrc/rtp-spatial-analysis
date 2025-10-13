import configuration
import yaml
from pathlib import Path
import demo
import density_and_freight
import frequent_transit_routes_and_signal
import transit_stop_intersections
import getpass
import paratransit_bnd

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

if config['run_frequent_transit_routes_and_signal']:
    frequent_transit_routes_and_signal.run(config)
    
if config['run_transit_stop_intersections']:
    transit_stop_intersections.run(config)

if config['run_paratransit_boundary']:
    paratransit_bnd.run(config)    
