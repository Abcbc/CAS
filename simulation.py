from utils.Logger import *
log = get_logger(__name__, __file__) # For Main

import networkx as nx
#import matplotlib.pyplot as plt

def main():
    print("First Commit")
    log.debug("First Commit")
    
    graph = nx.complete_graph(2)
    
    #plt.figure()
    #nx.draw(graph,with_labels=True)
    #plt.show()
    
    graph.node[0]['xname'] = 'Peter'
    graph.node[1]['xname'] = 'Karl'
    
#     print(graph.node)
#     
#     print(graph.node[0])
#     
#     for key in graph.node[0]:
#         print('"'+key+'": '+graph.node[0][key])
    
    graph.edges[0,1]['concatname'] = "PeterKarl"
    
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
        newNode['xname'] = oldNode['xname']+str(0)
        
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
    main()
