import utils.ConfigLoader as cnf
from ConvergensChecker import ConvergensChecker
from GraphFactory import GraphFactory
import networkx as nx

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
import Builder
import Updater
import GraphLog as gl
import Rules
import Analyser


def run_simulation(simulation_setting):
    log.debug(simulation_setting)
    gf = GraphFactory(simulation_setting)
    g = gf.create()

    updater = Updater.Updater()
    updater.setGraph(g)

    convegens_checker = ConvergensChecker(simulation_setting)
    analyser = Analyser.Analyser()
    analyser.initAnalysis(g)


    for rulename, rule in Rules.getRuleset().items():
        rule.setParameters(simulation_setting['Rules'][rulename])

    for i in range(simulation_setting["sim_iterations"]):
        updater.update()
        if convegens_checker.converges(analyser.onNewVersion(g)):
            analyser.finishAnalysis(g)
            break


    updater.close()

    #gExe = g.GraphLogExecuter(gl.GraphLogReader('logs/graph.log'))
    #gExe.performSteps(20)


def main():
    log.info("Loading Config.")
    settings = cnf.load_config()
    for simulation_setting in settings:
        run_simulation(simulation_setting)

    log.debug("First Commit")

    graph = nx.complete_graph(3)

if __name__ == "__main__":
    main()
