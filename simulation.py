import utils.ConfigLoader as cnf

from utils.Logger import *
log = get_logger(__name__, __file__) # For Main, call before any include with also calls get_logger
from SelectionRules import *
from Builder import buildGraph, buildTestGraphForNewEdgeRule, buildTestGraphForTakeoverRule
from Rules import *
from utility import *
from Updater import Updater
from GraphLogEntries import GraphLogSnapshotEntry
from Graph import toJsonStr, fromJsonStr, toPickle, fromPickle, calculateAttributes
from GraphLogExecuter import GraphLogExecuter
from GraphLogReaders import GraphLogReaderJson
from Graph import calculateAttributes

import networkx as nx

if __name__ == "__main__":
    g = buildGraph()

    updater = Updater()
    updater.setGraph(g)

    for i in range(20):
        updater.update()

    updater.close()

    gExe = gl.GraphLogExecuter(gl.GraphLogReaderJson('logs/graph.log'))
    gExe = gl.GraphLogExecuter(gl.GraphLogReaderJson('logs/graph.log'))
    gExe.performSteps(20)
