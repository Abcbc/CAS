import utils.ConfigLoader as cnf

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main


def run_simulation(simulation_setting):
    print(simulation_setting)


def main():
    log.info("Loading Config.")
    settings = cnf.load_config()
    for simulation_setting in settings:
        run_simulation(simulation_setting)

    log.debug("First Commit")


if __name__ == "__main__":
    main()
