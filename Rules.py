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
    Returns a dictionary with parameters which are used in this rule
    '''
    def getParameters(self):
        raise NotImplementedError('getParameters not implemented for this rule class')

    '''
    Sets parameters from the dictionary (can be retrieved with getParameters)
    '''
    def setParameters(self, parameters):
        raise NotImplementedError('setParameters not implemented for this rule class')

    '''
    Returns the internal data generated during application of the rule
    '''
    def getInternals(self):
        raise NotImplementedError('getInternals not implemented for this rule class')

    '''
    Applies this rule to the operands of the graph.
    Parameters must be a dictionary according to the rule's needs. If the argument
    is not given, parameters given with setParameters are used. Parameters given by
    this argument are used only for the particular call and are not stored.
    Internals must be a dictionary according to the rule's needs. The stored information
    will typically include the objects to operade on and decisions which are needed for
    rule application. If it is not given, the data will be generated and be available
    with getInternals.
    Returns the graph, which can be a new object.
    '''
    def apply(self, graph, operands=None, parameters=None, internals=None):
        raise NotImplementedError('apply not implemented for this rule class')

'''
Parameters: None
'''
class OrientationConfirmationRule(Rule):
    defaultParameters = dict() # accessed by get/setParameters, used as fallback by apply
    parameters = dict() # actual parameters used during application.

    def getParameters(self):
        return self.defaultParameters

    def setParameters(self, parameters):
        for paramKey in self.defaultParameters:
            self.defaultParameters[paramKey] = parameters[paramKey]

    def _createInternals(self, graph):
        self.internals = {'fallbackDecision': [],
                           'fallbackSelection': [],
                           'edgeId': self._findOperands(graph)
                          }
        nodeA = graph.nodes[self.internals['edgeId'][0]]
        for i in range(len(nodeA[KEY_OPINIONS])):
            self.internals['fallbackDecision'].append( random.random() > self._calcProbability() )
            self.internals['fallbackSelection'].append( random.choice([0,1]) )


    def _findOperands(self, graph):
        return selectEdgeFromGraph(graph)

    def getInternals(self):
        return self.internals

    def _calcProbability(self):
        return 0.5

    # TODO this could look a lot prettier
    def apply(self, graph, _parameters=None, _internals=None):
        if _internals == None:
            self._createInternals(graph)
        else:
            self.internals = _internals
        self.parameters = _parameters if _parameters is not None else self.getParameters()

        nodeA = graph.nodes[self.internals['edgeId'][0]]
        nodeB = graph.nodes[self.internals['edgeId'][1]]
        opinionsA = nodeA[KEY_OPINIONS]
        opinionsB = nodeB[KEY_OPINIONS]

        for i in range(len(nodeA[KEY_OPINIONS])):
            if doOpinionsDiffer(opinionsA[i], opinionsB[i]):
                if self.internals['fallbackDecision'][i]:
                    if self.internals['fallbackSelection'][i] == 0:
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
    defaultParameters = dict() # accessed by get/setParameters, used as fallback by apply
    parameters = dict() # actual parameters used during application.

    def getParameters(self):
        return self.defaultParameters

    def setParameters(self, parameters):
        for paramKey in self.defaultParameters:
            self.defaultParameters[paramKey] = parameters[paramKey]

    def _createInternals(self, graph):
        self.internals = {'opinionPair': self._findOperands(graph)
                          }

    def _findOperands(self, graph):
        # ToDo always chooses the same edge with the weight_getter_edge lambda, why?
#         opinionPair =  SelectionRules.selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[KEY_ORIENTATION]), predicate=self._selectionPredicate)
        # this works
        return selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : 1, predicate=self._selectionPredicate, maxChoiceTries=1e6)

    def getInternals(self):
        return self.internals

    def _selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][KEY_OPINIONS][pair['opinionIndex']]
        return areOppositeOpinions(opA, opB)

    def apply(self, graph, _parameters=None, _internals=None):
        if _internals == None:
            self._createInternals(graph)
        else:
            self.internals = _internals
        self.parameters = _parameters if _parameters is not None else self.getParameters()

        # ToDo real behavior, this is only dummy and always changes nodeA
        nodeA = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeA']
        nodeB = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeB']
        nodeA[KEY_OPINIONS][self.internals['opinionPair']['opinionIndex']] += nodeB[KEY_OPINIONS][self.internals['opinionPair']['opinionIndex']]

        return graph

    @staticmethod
    def getName():
        return 'AdaptationRule'
