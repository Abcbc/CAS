import random
from SelectionRules import selectEdgeFromGraph, selectOpinionPairFromGraph
from Graph import KEY_OPINIONS, doOpinionsDiffer, areOppositeOpinions

def getRuleset():
    return {
        OrientationConfirmationRule.getName():OrientationConfirmationRule(),
        AdaptationRule.getName():AdaptationRule()
        }

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
    Clears internal parameters so that they will be generated new
    '''
    def clearParameters(self):
        raise NotImplementedError('clearParameters not implemented for this rule class')

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
        return self.parameters

    def setParameters(self, parameters):
        for paramKey in self.parameters:
            self.parameters[paramKey] = parameters[paramKey]

    def clearParameters(self):
        self.parameters = {'fallbackDecision': [],
                           'fallbackSelection': []}

    def getOperands(self, graph):
        print('Selecting operands for OrientationConfirmationRule')
        return selectEdgeFromGraph(graph)

    def _calcProbability(self):
        return 0.5

    def __init__(self):
        self.clearParameters()

    # TODO this could look a lot prettier
    def apply(self, graph, edgeId):
        print('Apply OrientationConfirmationRule')
        # how many times?
        # apply to all opinions or select one "opinion-pair"?
        nodeA = graph.nodes[edgeId[0]]
        nodeB = graph.nodes[edgeId[1]]
        opinionsA = nodeA[KEY_OPINIONS]
        opinionsB = nodeB[KEY_OPINIONS]

        for i in range(len(nodeA[KEY_OPINIONS])):
            if len(self.parameters['fallbackDecision']) <= i: # if this opinion no decision yet
                if random.random() > self._calcProbability():
                    self.parameters['fallbackDecision'].append(True)
                else:
                    self.parameters['fallbackDecision'].append(False)
            if len(self.parameters['fallbackSelection']) <= i:
                self.parameters['fallbackSelection'].append(random.choice([0,1]))

            if doOpinionsDiffer(opinionsA[i], opinionsB[i]):
                if self.parameters['fallbackDecision'][i]:
                    if self.parameters['fallbackSelection'][i] == 0:
                        opToChange = opinionsA
                    else:
                        opToChange = opinionsB
                    opToChange[i] = 0
                    #print('Change opinionpair ' + str(i) + ' in node ' + str(self.parameters['fallbackSelection'][i]) + ' of nodes ' + str(edgeId))

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

    def setParameters(self, parameters):
        pass

    def clearParameters(self):
        pass

    def getOperands(self, graph):
        print('Selecting operands for AdaptationRule')
        # ToDo always chooses the same edge with the weight_getter_edge lambda, why?
#         opinionPair =  SelectionRules.selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[KEY_ORIENTATION]), predicate=self._selectionPredicate)
        # this works
        return selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : 1, predicate=self._selectionPredicate, maxChoiceTries=1e6)

    def _selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][KEY_OPINIONS][pair['opinionIndex']]
        return areOppositeOpinions(opA, opB)

    def apply(self, graph, opinionPair):
        print('Apply AdaptationRule')
        # ToDo real behavior, this is only dummy and always changes nodeA
        nodeA = graph.edges[opinionPair['edgeId']] ['nodeA']
        nodeB = graph.edges[opinionPair['edgeId']] ['nodeB']
        nodeA[KEY_OPINIONS][opinionPair['opinionIndex']] += nodeB[KEY_OPINIONS][opinionPair['opinionIndex']]

        return graph

    @staticmethod
    def getName():
        return 'AdaptationRule'
