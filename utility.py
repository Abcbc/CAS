# import networkx as nx
# import matplotlib.pyplot as plt
# 
# def drawGraph(graph):
#     plt.figure()
#     nx.draw(graph)
#     plt.show()
import networkx as nx
from Graph import KEY_NODE_ID, KEY_OPINIONS, KEY_SPECTRUM, KEY_ORIENTATION

def printNode(node):
    print(
        str(node[KEY_NODE_ID]) + ': ' +
        'op: ' + str(node[KEY_OPINIONS]) + 
        ', spectrum: ' + str(node[KEY_SPECTRUM]))
    
def printEdge(edge):
    print(str(edge[KEY_ORIENTATION]))
    
def printGraph(graph):
    for nodeId in graph.nodes:
        printNode(graph.nodes[nodeId])
        for neighborId in graph.neighbors(nodeId):
            print('NeighId ' + str(neighborId) + ': orientation ' + str(graph.edges[nodeId,neighborId][KEY_ORIENTATION]))

def isDivisor(number, divisorCandidate):
    return isNull(number % divisorCandidate)

def isNull(float):
    return float < 1e-5
