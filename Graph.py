KEY_NODE_ID = 'id'
KEY_EDGE_ID = 'id'
KEY_SPECTRUM = 'spectrum'
KEY_OPINIONS = 'opinions'
KEY_ORIENTATION = 'orientation'
KEY_V = 'V'


def getEdgesFromIndices(graph, ids):
    edges = []
    for id in ids:
        edges.append(graph.edges[id])
    return edges

def calcSpectrum(opinions):
    spectrum = 0
    for op in opinions:
        spectrum += op*op
    
    return spectrum
        
def calcOrientation(nodeA, nodeB):
    orientation = 0
    for opA, opB in zip(nodeA[KEY_OPINIONS], nodeB[KEY_OPINIONS]):
        orientation += opA*opB
    orientation /= len(nodeA[KEY_OPINIONS])
    
    return orientation

def calcV(edges): # "anerkanntes Vermoegen"
    V = 0
    for edge in edges:
        V += edge[KEY_ORIENTATION] * edge[KEY_ORIENTATION]
    
    return V

def calculateAttributes(graph):
    for edgeId in graph.edges:
        edge = graph.edges[edgeId]
        neighborA = graph.nodes[edgeId[0]]
        neighborB = graph.nodes[edgeId[1]]
        edge[KEY_ORIENTATION] = calcOrientation(neighborA, neighborB)
        
    for nodeId in graph.nodes:
        node = graph.nodes[nodeId]
        node[KEY_SPECTRUM] = calcSpectrum(node[KEY_OPINIONS])
        
        edges = getEdgesFromIndices(graph, graph.edges(nodeId))
        node[KEY_V] = calcV(edges)
        
    return graph



def doOpinionsDiffer(opinionA, opinionB):
    # differ if both != 0 and not equal
    return opinionA*opinionB == -1

def areOppositeOpinions(opinionA, opinionB):
    # dif one is 1 and one is -1
    return opinionA*opinionB == -1
