import utils.ConfigLoader as cnf
from GraphFactory import GraphFactory
import networkx as nx
import multiprocessing as mp
import time

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
import Builder
import Updater
import GraphLog as gl
import Rules

def run_repetition(ruleset, graph, logDir, repetition, iterations):
    updater = Updater.Updater(ruleset)
    updater.setGraph(graph, get_graph_logger('GraphLogger_'+logDir+'graph_'+str(repetition), logDir+'graph_'+str(repetition)+'.log'))

    for iteration in range(iterations):
        updater.update()

    updater.close()

results = []

def run_simulation(simulation_setting, logDir, pool):
    log.debug(simulation_setting)
    gf = GraphFactory(simulation_setting)

    for repetition in range(simulation_setting["sim_repetitions"]):
        g = gf.create()

        ruleset = Rules.getNewRuleset()
        for rulename, rule in ruleset.items():
            rule.setParameters(simulation_setting[rulename])



    #gExe = g.GraphLogExecuter(gl.GraphLogReader('logs/graph.log'))
    #gExe.performSteps(20)

        results.append(pool.apply_async(run_repetition, args=(ruleset, g, logDir, repetition, simulation_setting["sim_iterations"])))

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
    # monitor progress
    ready = False
    while not ready:
        all = sum([1 for res in results])
        finished = sum([1 for res in results if res.ready()])
        print(str(finished) + ' of ' + str(all) + ' jobs finished')
        ready = (all <= finished)
        time.sleep(1)

    pool.join()

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print("time consumed: " + str(end-start) + " s")
