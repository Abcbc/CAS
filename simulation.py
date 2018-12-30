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

        ruleset = Rules.getNewRuleset()
        for rulename, rule in ruleset.items():
            rule.setParameters(simulation_setting[rulename])

        updater = Updater.Updater(ruleset)
        updater.setGraph(g, name='graph_'+str(repetition))

        for iteration in range(simulation_setting["sim_iterations"]):
            updater.update()

    updater.close()

    #gExe = g.GraphLogExecuter(gl.GraphLogReader('logs/graph.log'))
    #gExe.performSteps(20)


def main():
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
            run_simulation(stepConfig)

if __name__ == "__main__":
    main()
