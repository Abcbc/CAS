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

    for repetition in range(simulation_setting["sim_repetitions"]):
        g = gf.create()

        updater = Updater.Updater()
        updater.setGraph(g, name='graph_'+str(repetition))

        for rulename, rule in Rules.getRuleset().items():
            rule.setParameters(simulation_setting[rulename])

        for iteration in range(simulation_setting["sim_iterations"]):
            updater.update()

    updater.close()

    #gExe = g.GraphLogExecuter(gl.GraphLogReader('logs/graph.log'))
    #gExe.performSteps(20)


def main():
    log.info("Loading Config.")
    settings = cnf.load_config()
    for simulation_setting in settings:
        stepConfigs = cnf.get_iteration_steps(simulation_setting)
        for stepConfig in stepConfigs:
            run_simulation(stepConfig)

if __name__ == "__main__":
    main()
