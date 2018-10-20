import random
from SelectionRules import selectEdgeFromGraph, selectOpinionPairFromGraph
from Graph import KEY_OPINIONS, doOpinionsDiffer, areOppositeOpinions

class Rule:
    '''
    Returns the human-readable and unique name for this rule
    '''
    @staticmethod
    def getName():
        raise NotImplementedError('getName not implemented for this rule class')

    '''
    Returns a dictionary with internal parameters which are used in this rule
    '''
    def getParameters(self):
        raise NotImplementedError('getParameters not implemented for this rule class')

    '''
    Sets internal parameters from the dictionary (can be retrieved with getParameters)
    '''
    def setParameters(self, parameters):
        raise NotImplementedError('setParameters not implemented for this rule class')

    '''
    Returns the operands to be passed to apply()
    '''
    def getOperands(self, graph):
        raise NotImplementedError('getOperands not implemented for this rule class')

    '''
    Applies this rule to the operands of the graph.
    Operands have to be parts of the graph and have the structure as returned by getOperands().
    Returns the graph, which can be a new object.
    '''
    def apply(self, graph, operands):
        raise NotImplementedError('apply not implemented for this rule class')

'''
Parameters: None
'''
class OrientationConfirmationRule(Rule):
    def getParameters(self):
        return dict()

    def getOperands(self, graph):
        print('Selecting operands for OrientationConfirmationRule')
        return selectEdgeFromGraph(graph)

    def _calcProbability(self):
        return 0.5

    def apply(self, graph, edgeId):
        print('Apply OrientationConfirmationRule')
        # how many times?
        # apply to all opinions or select one "opinion-pair"?
        nodeA = graph.nodes[edgeId[0]]
        nodeB = graph.nodes[edgeId[1]]
        opinionsA = nodeA[KEY_OPINIONS]
        opinionsB = nodeB[KEY_OPINIONS]
        
        #print('nodes: ' + str(edgeId))
        for i in range(len(nodeA[KEY_OPINIONS])):
            if doOpinionsDiffer(opinionsA[i], opinionsB[i]):
                #print('opinions['+str(i)+'] differ')
                if random.random() > self._calcProbability():
                    print('one opinion is going to fall back to neutral')
                    opToChange = random.choice([opinionsA, opinionsB])
                    opToChange[i] = 0

        return graph

    @staticmethod
    def getName():
        return 'OrientationConfirmationRule'

'''
Parameters: None
'''
class AdaptationRule(Rule):
    def getParameters(self):
        return dict()

    def getOperands(self, graph):
        print('Selecting operands for AdaptationRule')
        # ToDo always chooses the same edge with the weight_getter_edge lambda, why?
#         opinionPair =  SelectionRules.selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[KEY_ORIENTATION]), predicate=self._selectionPredicate)
        # this works
        return selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : 1, predicate=self._selectionPredicate)

    def _selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][KEY_OPINIONS][pair['opinionIndex']]
        return areOppositeOpinions(opA, opB)

    def apply(self, graph, opinionPair):
        print('Apply AdaptationRule')
        # ToDo real behavior, this is only dummy and always changes nodeA
        nodeA = opinionPair['edge']['nodeA']
        nodeB = opinionPair['edge']['nodeB']
        nodeA[KEY_OPINIONS][opinionPair['opinionIndex']] += nodeB[KEY_OPINIONS][opinionPair['opinionIndex']]

        return graph

    @staticmethod
    def getName():
        return 'AdaptationRule'
