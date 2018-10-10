import networkx as nx

def buildGraph():
    g = nx.complete_graph(3)
    for nodeId in g.node:
        #print(nodeId)
        g.nodes()[nodeId]['id']=nodeId
        g.nodes()[nodeId]['graph']=g
        g.nodes()[nodeId]['opinions']=[0,0,0]
        g.nodes()[nodeId]['spectrum']=0
    
    for edgeId in g.edges():
        #print(nodeId)
        g.edges()[edgeId]['id']=edgeId
        g.edges()[edgeId]['graph']=g
        g.edges()[edgeId]['orientation']=0
        
    return g