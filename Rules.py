import random
from SelectionRules import selectEdgeFromGraph, selectOpinionPairFromGraph
from Graph import KEY_OPINIONS, doOpinionsDiffer, areOppositeOpinions
from utils.Logger import get_logger

log = get_logger("Rule")

def getRuleset():
    return {
        OrientationConfirmationRule.getName():OrientationConfirmationRule(),
        AdaptationRule.getName():AdaptationRule()
        }

class Rule:
    """
    Base class for implementing rules

    Defines methods common to all classes and defines rule-specific methods with
    a NotImplementedError.

    Member variable: defaultParameters (dict):
        Default parameters. Can be changed by setParameters() and retrieved by
        getParameters(). Used to initialize parameters if none are given in apply()
        If a rule has parameters, it has to initialize them here,
    Member variable: parameters (dict):
        Actual parameters used during application. Set from the given parameters
        or the defaults.
    """

    defaultParameters = dict()

    parameters = dict()

    @staticmethod
    def getName():
        """
        Returns the human-readable and unique name for this rule
        """
        raise NotImplementedError('getName not implemented for this rule class')

    def getParameters(self):
        """
        Returns a dictionary with parameters which are used in this rule
        """
        return self.defaultParameters

    def setParameters(self, parameters):
        """
        Sets parameters from the dictionary (can be retrieved with getParameters)
        """
        for paramKey in self.defaultParameters:
            self.defaultParameters[paramKey] = parameters[paramKey]

    def getInternals(self):
        """
        Returns the internal data generated during application of the rule
        """
        return self.internals

    def _createInternals(self, graph):
        """
        Creates and returns the internal data
        """
        raise NotImplementedError('_createInternals not implemented for this rule class')

    def _prepareApply(self, graph, _parameters, _internals):
        """
        Internal method. Common for all rule classes. Initializes operands, parameters and internals.
        """
        self.parameters = _parameters if _parameters is not None else self.getParameters()
        self.internals = _internals if _internals is not None else  self._createInternals(graph)

    def apply(self, graph, operands=None, parameters=None, internals=None):
        """
        Applies this rule to the operands of the graph.
        Parameters must be a dictionary according to the rule's needs. If the argument
        is not given, parameters given with setParameters are used. Parameters given by
        this argument are used only for the particular call and are not stored.
        Internals must be a dictionary according to the rule's needs. The stored information
        will typically include the objects to operade on and decisions which are needed for
        rule application. If it is not given, the data will be generated and be available
        with getInternals.
        Returns the graph, which can be a new object.
        """
        raise NotImplementedError('apply not implemented for this rule class')

class OrientationConfirmationRule(Rule):
    """
    fallbackProbability: probability for each of the differing opinion pairs to
    fall to neutral on one side. Range: 0 to 1. Default: 0.5.
    """

    defaultParameters = {'fallbackProbability': 0.5}

    def _createInternals(self, graph):
        self.internals = {'fallbackDecision': [],
                           'fallbackSelection': [],
                           'edgeId': self._findOperands(graph)
                          }
        nodeA = graph.nodes[self.internals['edgeId'][0]]
        for i in range(len(nodeA[KEY_OPINIONS])):
            self.internals['fallbackDecision'].append( random.random() > self._calcProbability() )
            self.internals['fallbackSelection'].append( random.choice([0,1]) )

        return self.internals

    def _findOperands(self, graph):
        return selectEdgeFromGraph(graph)

    def _calcProbability(self):
        return self.parameters['fallbackProbability']

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph, _parameters, _internals)
        log.debug('applying OrientationConfirmationRule with parameters ' +
                  str(self.parameters) + ' and internals ' + ('(given) ' if _parameters is not None else '') +
                  str(self.internals) + (' (given)' if _internals is not None else ''))

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

        return graph

    @staticmethod
    def getName():
        return 'OrientationConfirmationRule'

'''
Parameters: None
'''
class AdaptationRule(Rule):
    def _createInternals(self, graph):
        self.internals = {'opinionPair': self._findOperands(graph)
                          }
        return self.internals

    def _findOperands(self, graph):
        # ToDo always chooses the same edge with the weight_getter_edge lambda, why?
#         opinionPair =  SelectionRules.selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[KEY_ORIENTATION]), predicate=self._selectionPredicate)
        # this works
        return selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : 1, predicate=self._selectionPredicate, maxChoiceTries=1e6)

    def _selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][KEY_OPINIONS][pair['opinionIndex']]
        return areOppositeOpinions(opA, opB)

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph, _parameters, _internals)
        log.debug('applying AdaptationRule with parameters ' +
                  str(self.parameters) + ' and internals ' + ('(given) ' if _parameters is not None else '') +
                  str(self.internals) + (' (given)' if _internals is not None else ''))

        # ToDo real behavior, this is only dummy and always changes nodeA
        nodeA = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeA']
        nodeB = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeB']
        nodeA[KEY_OPINIONS][self.internals['opinionPair']['opinionIndex']] += nodeB[KEY_OPINIONS][self.internals['opinionPair']['opinionIndex']]

        return graph

    @staticmethod
    def getName():
        return 'AdaptationRule'
