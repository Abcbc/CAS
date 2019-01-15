import utils.ConfigLoader as cnf
from GraphFactory import GraphFactory
import networkx as nx
import multiprocessing as mp
import time
import matplotlib.pyplot as plt
import csv
import numpy as np

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
import Builder
import Updater
import GraphLog as gl
import Rules

import matplotlib.pyplot as plt
# Note on concurrent simulation: repetition-level concurrency would be the solution that offers
# speedup in all cases (provided with more than one core, of course). But I do not know if the
# jobs are executed in the same order as they are given to apply_async. If they are not, with
# bad execution orders (when all the last repetition of every step are the last jobs to get
# executed), all results have to be kept im memory before the mean and std of all repetitions of
# one step can be computed. In the extreme case,
# <number_of_steps>*<repetitions>*<number_of_metrics>*<number_of_iterations> = a lot
# of datapoints have to be stored in memory.
# So I implemented concurrency in step level, which yields no speedup if many repetitions of
# only few steps are needed.

# The results are stored in  structures/files as follows:
# results[<sim_name>]: -'dir': string, directory for files for this simulation
#                      - 'steps': list of - 'settings': dict
#                                         - 'result': result object of dict - 'mean': dict metric_name->data
#                                                                           - 'std': dict metric_name->data
#                                         - 'stepDir': string, directory for this simulation step
# The full simulation data can be written to disk in the following directory structure:
# experiment/<sim_name>/<step_number>/ contains graph_<repetition>.log, graph_<repetition>.csv, settings.yaml,
# metrics_mean.csv, metrics_std.csv
# Especially the graph logs may grow large and numerous, so graph logging can be disabled  in de updater.
# The graph csv files can be turned off by commenting out the respective lines in finish_simulation.

def run_repetition(ruleset, config, graph, logDir, repetition):
    updater = Updater.Updater(ruleset, config)
    updater.setGraph(graph, get_graph_logger('GraphLogger_'+logDir+'graph_'+str(repetition), logDir+'graph_'+str(repetition)+'.log'))

    for iteration in range(config["sim_iterations"]):
        updater.update()

    updater.close()

    return {
        'log': logDir+'graph_'+str(repetition)+'.log',
        'analyzer': updater.getAnalyzer(),
    }

def finish_simulation(simulation_setting, repetitions, logDir):
    analyzers = [rep['analyzer'] for rep in repetitions]

    cnf.save_config(simulation_setting,  logDir+'settings.yaml')

    # write graph metrics to csv
    for ind, analyser in enumerate(analyzers):
        analyser.write(logDir+'graph_'+str(ind)+'.csv')

    # build mean and std over all analyzers
    metrics_mean = []
    metrics_std = []
    metrics_mean.append(analyzers[0].results['Version'])
    metrics_std.append(analyzers[0].results['Version'])
    for metric in analyzers[0].metrics:
        if metric.getMetricName() is not 'Version':
            metric_combined = np.array([analyser.results[metric.getMetricName()] for analyser in analyzers]) # a row is an analyzer
            metrics_mean.append(np.mean(metric_combined, axis=0))
            metrics_std.append(np.std(metric_combined, axis=0))

    for suffix, contents in zip(['mean','std'], [metrics_mean, metrics_std]):
        combinedCsv = csv.writer(open(logDir+'metrics_'+suffix+'.csv','w'))
        combinedCsv.writerow([metric.getMetricName() for metric in analyzers[0].metrics])
        for i in range(len(analyzers[0].results['Version'])):
            row = []
            for row_contents in contents:
                row.append(row_contents[i])
            combinedCsv.writerow(row)

    mean = {metric.getMetricName():metrics_mean[i] for i, metric in enumerate(analyzers[0].metrics)}
    std = {metric.getMetricName():metrics_std[i] for i, metric in enumerate(analyzers[0].metrics)}

    return {'mean':mean,
            'std':std,
            }

def run_simulation(simulation_setting, logDir):
    log.debug(simulation_setting)
    gf = GraphFactory(simulation_setting)
    repetitions = []

    for repetition in range(simulation_setting["sim_repetitions"]):
        g = gf.create()

        ruleset = {name:rule for name, rule in Rules.getNewRuleset().items()}
        for rule in ruleset.values():
            rule.setParameters(simulation_setting)

        repetitions.append(run_repetition(ruleset, simulation_setting, g, logDir, repetition))

    return finish_simulation(simulation_setting, repetitions, logDir)

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

            stepResult = pool.apply_async(run_simulation, args=(stepConfig.copy(), stepDir))

            results[simulation_setting['sim_name']]['steps'].append({
                'settings':stepConfig,
                'result': stepResult,
                'stepDir': stepDir,
            })

    pool.close()
    # monitor progress
    ready = False
    while not ready:
        all = sum([step['settings']['sim_repetitions'] for sim in results.values() for step in sim['steps']])
        finished = sum([step['settings']['sim_repetitions'] for sim in results.values() for step in sim['steps'] if step['result'].ready()])
        print(str(finished) + ' of ' + str(all) + ' jobs finished')
        ready = (all <= finished)
        try:
            time.sleep(1)
        except:
            pass

    if  sum([not step['result'].successful() for sim in results.values() for step in sim['steps']]) > 0:
        log.error('an exception occurrent in a simulation')

    pool.join()


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
