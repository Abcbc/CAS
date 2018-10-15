from SelectionRules import *
import networkx as nx
import random

KEY_SPECTRUM = 'spectrum'
KEY_OPINIONS = 'opinions'
KEY_ORIENTATION = 'orientation'
KEY_V = 'V'

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

def getEdgesFromIndices(graph, ids):
    edges = []
    for id in ids:
        edges.append(graph.edges[id])
    return edges

def doOpinionsDiffer(opinionA, opinionB):
    # differ if both != 0 and not equal
    return opinionA*opinionB == -1

def areOppositeOpinions(opinionA, opinionB):
    # dif one is 1 and one is -1
    return opinionA*opinionB == -1

class AttributesUpdateRule:
#     graph = nx.Graph()
#     selectionRule = selectNodeFromGraph(graph)
    def apply(self, graph): # TODO: not the rule should have the apply method?
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
    
class OrientationConfirmationRule:
    def calcProbability(self):
        return 0.5
        
    def apply(self, graph):
        # how many times?
        # apply to all opinions or select one "opinion-pair"?
        edgeId = selectEdgeFromGraph(graph)
        edge = graph.edges[edgeId]
        nodeA = graph.nodes[edgeId[0]]
        nodeB = graph.nodes[edgeId[1]]
        opinionsA = nodeA[KEY_OPINIONS]
        opinionsB = nodeB[KEY_OPINIONS]
        
        #print('nodes: ' + str(edgeId))
        for i in range(len(nodeA[KEY_OPINIONS])):
            if doOpinionsDiffer(opinionsA[i], opinionsB[i]):
                #print('opinions['+str(i)+'] differ')
                if random.random() > self.calcProbability():
                    print('one opinion is going to fall back to neutral')
                    opToChange = random.choice([opinionsA, opinionsB])
                    opToChange[i] = 0
                    
class AdaptationRule:
    def selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][KEY_OPINIONS][pair['opinionIndex']]
        return areOppositeOpinions(opA, opB)
        
    def apply(self, graph):
        # ToDo always chooses the same edge with the weight_getter_edge lambda, why?
        #opinionPair =  SelectionRules.selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[KEY_ORIENTATION]), predicate=self.selectionPredicate)
        # this works
        opinionPair =  selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : 1, predicate=self.selectionPredicate)
        
        # ToDo real behavior, this is only dummy and always changes nodeA
        nodeA = opinionPair['edge']['nodeA']
        nodeB = opinionPair['edge']['nodeB']
        nodeA[KEY_OPINIONS][opinionPair['opinionIndex']] += nodeB[KEY_OPINIONS][opinionPair['opinionIndex']]
