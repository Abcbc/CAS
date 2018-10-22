import utils.ConfigLoader as cnf

from utils.Logger import *
from SelectionRules import *
from Builder import buildGraph
from Rules import *
from utility import *
from Updater import Updater
from GraphLogEntries import GraphLogSnapshotEntry
from Graph import toJsonStr, fromJsonStr, toPickle, fromPickle
from GraphLogExecuter import GraphLogExecuter
from GraphLogReaders import GraphLogReaderJson
log = get_logger(__name__, __file__) # For Main

import networkx as nx
#import matplotlib.pyplot as plt

def run_simulation(simulation_setting):
    print(simulation_setting)


def main():
    log.info("Loading Config.")
    settings = cnf.load_config()
    for simulation_setting in settings:
        run_simulation(simulation_setting)

    log.debug("First Commit")
    
    graph = nx.complete_graph(3)
    
    #plt.figure()
    #nx.draw(graph,with_labels=True)
    #plt.show()
    
    graph.node[0]['xname'] = 'Peter'
    graph.node[1]['xname'] = 'Karl'
    graph.node[2]['xname'] = 'Alice'
    
#     print(graph.node)
#     
#     print(graph.node[0])
#     
#     for key in graph.node[0]:
#         print('"'+key+'": '+graph.node[0][key])
    
    graph.edges[0,1]['concatname'] = "PeterKarl"
    graph.remove_edge(0,2)
    
    #print(graph.edges[0,1]['nodes'])
    
    for edgeId in graph.edges:
        print('edgeId: '+str(edgeId))
        for key in graph.edges[edgeId]:
            print('"'+key+'": '+str(graph.edges[edgeId][key]))
    

    newGraph = nx.Graph()
    # update nodes
    for nodeId in graph.node:
        print('updating node '+str(nodeId))
        oldNode = graph.node[nodeId]
        newGraph.add_node(nodeId)
        newNode = newGraph.node[nodeId]
        numberOfNeighbors = len(list(graph.neighbors(nodeId)))
        appendix = ''
        for neighborId in list(graph.neighbors(nodeId)):
            neighbor = graph.node[neighborId]
            appendix = appendix + neighbor['xname'][0]
        newNode['xname'] = oldNode['xname']+str(numberOfNeighbors)+appendix
        
    # update edges




    print()
    print()
    print()
    print('Old graph:')
    for nodeId in graph.node:
        print('nodeID: '+str(nodeId))
        for key in graph.node[nodeId]:
            print('"'+key+'": '+graph.node[nodeId][key])
    
    print()
    print()
    print()
    print('New graph:')
    for nodeId in newGraph.node:
        print('nodeID: '+str(nodeId))
        for key in newGraph.node[nodeId]:
            print('"'+key+'": '+newGraph.node[nodeId][key])
            
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
