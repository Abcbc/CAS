from utils.Logger import *
from SelectionRules import *
from Builder import *
from Rules import *
from utility import *
log = get_logger(__name__, __file__) # For Main

import networkx as nx
#import matplotlib.pyplot as plt

def main():
    print("First Commit")
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

if __name__ == "__main__":
    g = buildGraph()
    
    print('Original graph')
    printGraph(g)
    
    aur = AttributesUpdateRule()
    #g = aur.apply(g)
    aur.apply(g)
    
    print('')
    print('')
    print('')
    print('Graph with attributes')
    printGraph(g)
    
    ocr = OrientationConfirmationRule()
    ocr.apply(g)
    
    print('')
    print('')
    print('')
    print('Graph with attributes')
    printGraph(g)
    