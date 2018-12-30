import utils.ConfigLoader as cnf
from GraphFactory import GraphFactory
import networkx as nx

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
import Builder
import Updater
import GraphLog as gl
import Rules


def run_simulation(simulation_setting):
    log.debug(simulation_setting)
    gf = GraphFactory(simulation_setting)
    g = gf.create()

    updater = Updater.Updater()
    updater.setGraph(g)

    for rulename, rule in Rules.getRuleset().items():
        rule.setParameters(simulation_setting['Rules'][rulename])

    for i in range(simulation_setting["sim_iterations"]):
        updater.update()

    updater.close()

    #gExe = g.GraphLogExecuter(gl.GraphLogReader('logs/graph.log'))
    #gExe.performSteps(20)


def main():
    log.info("Loading Config.")
    settings = cnf.load_config()
    for simulation_setting in settings:
        run_simulation(simulation_setting)

if __name__ == "__main__":
    main()
