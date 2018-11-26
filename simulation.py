import utils.ConfigLoader as cnf

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
import Builder
import Updater
import GraphLog as gl

if __name__ == "__main__":
    g = Builder.buildGraph()

    updater = Updater.Updater()
    updater.setGraph(g)

    for i in range(20):
        updater.update()

    updater.close()

    gExe = gl.GraphLogExecuter(gl.GraphLogReaderJson('logs/graph.log'))
    gExe = gl.GraphLogExecuter(gl.GraphLogReaderJson('logs/graph.log'))
    gExe.performSteps(20)
