import yaml as yml
import os
from utils.Logger import *
log = get_logger(__name__, __file__) # For Main

def load_config():
    config = yml.load(open("\\".join([os.getcwd(), "configs", "simulations.yml"]), "r")).get("simulation_settings")
    defaults = config.get("defaults")
    result = [config[x] for x in config if x != "defaults"]
    print(result)
    for default_key in defaults:
        print(default_key)
        for e in result:
            if e.get(default_key) is None:
                e.update({default_key: defaults.get(default_key)})


    return result

def run_simulation(simulation_setting):
    print(simulation_setting)



def main():
    log.info("Loading Config.")
    settings = load_config()
    for simulation_setting in settings:
        run_simulation(simulation_setting)



    log.debug("First Commit")


if __name__ == "__main__":
    main()
