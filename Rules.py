from SelectionRules import *
import networkx as nx

KEY_SPECTRUM = 'spectrum'
KEY_OPINIONS = 'opinions'
KEY_ORIENTATION = 'orientation'

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

class AttributesUpdateRule:
#     graph = nx.Graph()
#     selectionRule = selectNodeFromGraph(graph)
    def apply(self, graph): # TODO: not the rule should have the apply method?
        for nodeId in graph.nodes:
            node = graph.nodes[nodeId]
            node[KEY_SPECTRUM] = calcSpectrum(node[KEY_OPINIONS])
            
        for edgeId in graph.edges:
            edge = graph.edges[edgeId]
            neighborA = graph.nodes[edgeId[0]]
            neighborB = graph.nodes[edgeId[1]]
            edge[KEY_ORIENTATION] = calcOrientation(neighborA, neighborB)
            
        return graph