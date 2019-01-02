import utils.ConfigLoader as cnf
from GraphFactory import GraphFactory
import networkx as nx
import multiprocessing as mp
import time
import matplotlib.pyplot as plt

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

    return {
        'log': logDir+'graph_'+str(repetition)+'.log',
        'analyzer': updater.getAnalyzer(),
    }

def run_simulation(simulation_setting, logDir, pool):
    log.debug(simulation_setting)
    gf = GraphFactory(simulation_setting)
    repetitions = []

    for repetition in range(simulation_setting["sim_repetitions"]):
        g = gf.create()

        ruleset = Rules.getNewRuleset()
        for rulename, rule in ruleset.items():
            rule.setParameters(simulation_setting[rulename])



        repetitions.append(pool.apply_async(run_repetition, args=(ruleset, g, logDir, repetition, simulation_setting["sim_iterations"])))
    return repetitions

def main():
    pool = mp.Pool()

    log.info("Loading Config.")
    settings = cnf.load_config()
    results = {}
    for simulation_setting in settings:
        simulation_dir = './experiment/' + simulation_setting['sim_name'] + '/'
        try:
            os.makedirs(simulation_dir)
        except(FileExistsError):
            pass
        cnf.save_config(simulation_setting, simulation_dir+'settings.yaml')

        stepConfigs = cnf.get_iteration_steps(simulation_setting)
        results[simulation_setting['sim_name']] = {
            'dir': simulation_dir,
            'steps': [],
        }
        for ind, stepConfig in enumerate(stepConfigs):
            stepDir = simulation_dir + str(ind) + '/'
            try:
                os.mkdir(stepDir)
            except(FileExistsError):
                pass
            cnf.save_config(stepConfig,  stepDir+'settings.yaml')
            repetitions = run_simulation(stepConfig, stepDir, pool)

            results[simulation_setting['sim_name']]['steps'].append({
                'settings':stepConfig,
                'repetitions': repetitions,
                'stepDir': stepDir,
            })

    pool.close()
    # monitor progress
    ready = False
    while not ready:
        all = sum([1 for sim in results.values() for step in sim['steps'] for rep in step['repetitions']])
        finished = sum([1 for sim in results.values() for step in sim['steps'] for rep in step['repetitions'] if rep.ready()])
        print(str(finished) + ' of ' + str(all) + ' jobs finished')
        ready = (all <= finished)
        time.sleep(1)

    pool.join()

    for name, sim in results.items():
        try:
            os.mkdir(sim['dir'] + 'img/')
        except FileExistsError:
            pass
        for step in sim['steps']:
            if  sum([not rep.successful() for rep in step['repetitions']]) > 0:
                log.error('an exception occurrent in a simulation')
            analyzers = [rep.get()['analyzer'] for rep in step['repetitions']]

            for metric in analyzers[0].metrics:
                plt.figure()
                for ind, analyser in enumerate(analyzers):
                    metric.plot(plt, analyser.results['Version'], analyser.results[metric.getMetricName()],label=str(ind))
                plt.legend(loc='upper left')
                plt.savefig(sim['dir'] + 'img/' + metric.getMetricName() + '.png')

            changedGraphsCnt = 0
            for analyser in analyzers:
                if analyser.results['GraphSize'][0] != analyser.results['GraphSize'][-1]:
                    changedGraphsCnt += 1
            print('percentage abweichler: '+str(step['settings']['tmp_percentage']))
            print('percentage changed graphs: '+str(changedGraphsCnt/simulation_setting['sim_repetitions']))

def run_from_log():
    logfile = '.log'
    import GraphLog as gl
    gExe = gl.GraphLogExecuter(gl.GraphLogReader(logfile))
    g = gExe.getGraph()

    plt.figure()
    nx.draw_networkx(gExe.getGraph())
    plt.title('before')

    gExe.performFullSimulation()

    plt.figure()
    nx.draw_networkx(gExe.getGraph())
    plt.title('after')

    for metric in gExe.getAnalyzer().metrics:
        plt.figure()
        metric.plot(plt, gExe.getAnalyzer().results['version'],gExe.getAnalyzer().results[metric.getMetricName()])

    plt.show()

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    end = time.perf_counter()
    print("time consumed: " + str(end-start) + " s")
