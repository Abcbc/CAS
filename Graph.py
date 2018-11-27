import networkx as nx
import json

KEY_NODE_ID = 'id'
KEY_EDGE_ID = 'id'
KEY_SPECTRUM = 'spectrum'
KEY_OPINIONS = 'opinions'
KEY_ORIENTATION = 'orientation'
KEY_V = 'V'
KEY_VERSION = 'version'

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

def removeConvenienceAttributes(graph):
    for nodeId in graph.nodes:
        node = graph.nodes[nodeId]
        del node['graph']
        del node[KEY_NODE_ID]

    for edgeId in graph.edges:
        edge = graph.edges[edgeId]
        del edge['graph']
        del edge[KEY_EDGE_ID]
        del edge['nodeA']
        del edge['nodeB']

    return graph

def addConvenienceAttributes(graph):
    for nodeId in graph.nodes:
        node = graph.nodes[nodeId]
        node['graph'] = graph
        node[KEY_NODE_ID] = nodeId

    for edgeId in graph.edges:
        edge = graph.edges[edgeId]
        edge['graph'] = graph
        edge[KEY_EDGE_ID] = edgeId
        edge['nodeA'] = graph.nodes[edgeId[0]]
        edge['nodeB'] = graph.nodes[edgeId[1]]

    return graph

def getMaxNodeId(graph):
    maxNodeId = 0
    for id in graph.nodes:
        maxNodeId = max(maxNodeId, id)
    return maxNodeId

def getNextNodeId(graph):
    return getMaxNodeId(graph) + 1

def createNewNodeSkeleton(graph):
    return { 'graph' : graph, KEY_NODE_ID : getNextNodeId(graph)}

def createNewEdgeSkeleton(graph, nodeA, nodeB):
    return { 'graph' : graph, KEY_EDGE_ID : (nodeA[KEY_NODE_ID],nodeB[KEY_NODE_ID]),
             'nodeA' : nodeA, 'nodeB': nodeB }

def toJsonStr(graph):
    return nx.jit_data(removeConvenienceAttributes(graph.copy()))

def fromJsonStr(jsonStr):
    return addConvenienceAttributes(nx.jit_graph(json.loads(jsonStr)))

def toPickle(graph, filename):
    nx.write_gpickle(removeConvenienceAttributes(graph.copy()),filename)

def fromPickle(filename):
    return addConvenienceAttributes(nx.read_gpickle(filename))
