import configuration
import yaml
from pathlib import Path
import demo

file = Path().joinpath(configuration.args.configs_dir, "config.yaml")

config = yaml.safe_load(open(file))

if config['run_demo']:
    demo.run(config)
    
