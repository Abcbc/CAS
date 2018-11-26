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
            
def testGraphLogWriteRead():
    g = buildGraph()

    j = toJsonStr(g)

    g2 = fromJsonStr(j)

    for nodeId in g.nodes:
        node = g.nodes[nodeId]
        node2 = g2.nodes[nodeId]
        if node[KEY_NODE_ID] != node2[KEY_NODE_ID] or node[KEY_OPINIONS] != node2[KEY_OPINIONS] or node[KEY_SPECTRUM] != node2[KEY_SPECTRUM]:
            return False
    for edgeId in g.edges:
        edge = g.edges[edgeId]
        edge2 = g2.edges[edgeId]
        if edge[KEY_EDGE_ID] != edge2[KEY_EDGE_ID] or edge[KEY_ORIENTATION] != edge2[KEY_ORIENTATION]:
            return False

    return True

if __name__ == "__main__":
    g = buildGraph()

    updater = Updater()
    updater.setGraph(g)

    for i in range(20):
        updater.update()

    updater.close()

    gExe = GraphLogExecuter(GraphLogReaderJson('logs/graph.log'))
    gExe.performSteps(20)
