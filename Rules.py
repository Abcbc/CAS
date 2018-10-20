import random
from SelectionRules import selectEdgeFromGraph, selectOpinionPairFromGraph
from Graph import KEY_OPINIONS, doOpinionsDiffer, areOppositeOpinions
    
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

        return graph

    @staticmethod
    def getName():
        return 'OrientationConfirmationRule'
                    
class AdaptationRule:
    def selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][KEY_OPINIONS][pair['opinionIndex']]
        return areOppositeOpinions(opA, opB)
        
    def apply(self, graph):
        # ToDo always chooses the same edge with the weight_getter_edge lambda, why?
#         opinionPair =  SelectionRules.selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[KEY_ORIENTATION]), predicate=self.selectionPredicate)
        # this works
        selectOpinionPairFromGraph(graph)
        opinionPair = selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : 1, predicate=self.selectionPredicate)
        
        # ToDo real behavior, this is only dummy and always changes nodeA
        nodeA = opinionPair['edge']['nodeA']
        nodeB = opinionPair['edge']['nodeB']
        nodeA[KEY_OPINIONS][opinionPair['opinionIndex']] += nodeB[KEY_OPINIONS][opinionPair['opinionIndex']]

        return graph

    @staticmethod
    def getName():
        return 'AdaptationRule'
