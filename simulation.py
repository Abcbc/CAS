import utils.ConfigLoader as cnf
from GraphFactory import GraphFactory
import networkx as nx
import multiprocessing as mp

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
import Builder
import Updater
import GraphLog as gl
import Rules

def _run(ruleset, graph, logDir, repetition, iterations):
    updater = Updater.Updater(ruleset)
    updater.setGraph(graph, get_graph_logger('GraphLogger_'+logDir+'graph_'+str(repetition), logDir+'graph_'+str(repetition)+'.log'))

    for iteration in range(iterations):
        updater.update()

    updater.close()


def run_simulation(simulation_setting, logDir, pool):
    log.debug(simulation_setting)
    gf = GraphFactory(simulation_setting)

    for repetition in range(simulation_setting["sim_repetitions"]):
        g = gf.create()

        ruleset = Rules.getNewRuleset()
        for rulename, rule in ruleset.items():
            rule.setParameters(simulation_setting[rulename])

        pool.apply_async(_run, args=(ruleset, g, logDir, repetition, simulation_setting["sim_iterations"]))


    #gExe = g.GraphLogExecuter(gl.GraphLogReader('logs/graph.log'))
    #gExe.performSteps(20)


def main():
    pool = mp.Pool()

    log.info("Loading Config.")
    settings = cnf.load_config()
    for simulation_setting in settings:
        simulation_dir = './experiment/' + simulation_setting['sim_name'] + '/'
        try:
            os.makedirs(simulation_dir)
        except(FileExistsError):
            pass
        cnf.save_config(simulation_setting, simulation_dir+'settings.yaml')

        stepConfigs = cnf.get_iteration_steps(simulation_setting)
        for ind, stepConfig in enumerate(stepConfigs):
            stepDir = simulation_dir + str(ind) + '/'
            try:
                os.mkdir(stepDir)
            except(FileExistsError):
                pass
            cnf.save_config(stepConfig,  stepDir+'settings.yaml')
            run_simulation(stepConfig, stepDir, pool)

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
