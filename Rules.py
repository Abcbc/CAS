import random
from SelectionRules import selectEdgeFromGraph, selectOpinionPairFromGraph
import Graph
from utils.Logger import get_logger
import community
import networkx as nx
import numpy as np

log = get_logger("Rule")

def getRuleset():
    return {
        OrientationConfirmationRule.getName():OrientationConfirmationRule(),
        AdaptationRule.getName():AdaptationRule(),
        NewNodeRule.getName():NewNodeRule(),
        NewEdgesRule.getName():NewEdgesRule(),
        RemoveEdgeRule.getName():RemoveEdgeRule(),
        TakeoverRule.getName():TakeoverRule(),
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

    def apply(self, graph, parameters=None, internals=None):
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
        if self.internals['edgeId'] is not None:
            nodeA = graph.nodes[self.internals['edgeId'][0]]
            for i in range(len(nodeA[Graph.KEY_OPINIONS])):
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

        if self.internals['edgeId'] is not None:
            nodeA = graph.nodes[self.internals['edgeId'][0]]
            nodeB = graph.nodes[self.internals['edgeId'][1]]
            opinionsA = nodeA[Graph.KEY_OPINIONS]
            opinionsB = nodeB[Graph.KEY_OPINIONS]

            for i in range(len(nodeA[Graph.KEY_OPINIONS])):
                if Graph.doOpinionsDiffer(opinionsA[i], opinionsB[i]):
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

class AdaptationRule(Rule):
    """
    Implementation of Adaptation Rule 2.1.2

    Parameters: None

    Chooses one pair of opinions -1 and 1 of nodes A and B. For this rule, the order of
    nodes in the edge is chosen randomly, as if the graph were directed.
    With probability V(B)/(V(A)+V(B)) the opinion of node A is set to the opinion at B.
    """
    def _createInternals(self, graph):
        self.internals = {'opinionPair': self._findOperands(graph),
                          'nodePosToAdapt': random.choice([0,1])
                          }
        self.internals['adaptionDecision'] = random.random() < self._calcAdaptionProbability(graph)
        return self.internals

    def _findOperands(self, graph):
        return selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge : abs(edge[Graph.KEY_ORIENTATION]), predicate=self._selectionPredicate, maxChoiceTries=1e6)

    def _selectionPredicate(self, pair):
        opA = pair['edge']['nodeA'][Graph.KEY_OPINIONS][pair['opinionIndex']]
        opB = pair['edge']['nodeB'][Graph.KEY_OPINIONS][pair['opinionIndex']]
        return Graph.areOppositeOpinions(opA, opB)

    def _calcAdaptionProbability(self, graph):
        nodeA = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeA']
        nodeB = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeB']
        nodeToAdapt = [nodeA, nodeB][self.internals['nodePosToAdapt']]
        nodeToAdaptFrom = [nodeB, nodeA][self.internals['nodePosToAdapt']]
        return nodeToAdaptFrom[Graph.KEY_V] / (nodeToAdapt[Graph.KEY_V]+nodeToAdaptFrom[Graph.KEY_V])

    def _adaptNodeToNode(self, toAdapt, toAdaptFrom):
        opInd = self.internals['opinionPair']['opinionIndex']
        toAdapt[Graph.KEY_OPINIONS][opInd] = toAdaptFrom[Graph.KEY_OPINIONS][opInd]

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph, _parameters, _internals)
        log.debug('applying AdaptationRule with parameters ' +
                  str(self.parameters) + ' and internals ' + ('(given) ' if _parameters is not None else '') +
                  str(self.internals) + (' (given)' if _internals is not None else ''))

        if self.internals['opinionPair'] is not None:
            if self.internals['adaptionDecision']:
                nodeA = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeA']
                nodeB = graph.edges[self.internals['opinionPair']['edgeId']] ['nodeB']
                nodeToAdapt = [nodeA, nodeB][self.internals['nodePosToAdapt']]
                nodeToAdaptFrom = [nodeB, nodeA][self.internals['nodePosToAdapt']]
                self._adaptNodeToNode(nodeToAdapt, nodeToAdaptFrom)

        return graph

    @staticmethod
    def getName():
        return 'AdaptationRule'

class NewNodeRule(Rule):
    """
    densityThreshold: minimum required n_edges/max possible n_edges
      for a community. Range: 0 to 1. Default: 0.8
    meanOrientationThreshold: minimum required mean of orientation in
      a community. Range: -1 to 1. Default: 0.8
    opMeanThreshold: minimum required mean of |orientation| in a community
      to give the new node an opinion. Range: 0 to 1. Default: 0.8
    """

    defaultParameters = { 'densityThreshold' : 0.8,
                          'meanOrientationThreshold' : 0.8,
                          'opMeanThreshold' : 0.8 }

    def _createInternals(self, graph):
        log.debug('NewNodeRule create internals')
        communities = self._findOperands(graph)
        self.internals = { 'nodesToAdd' : [] }
        for comm in communities:
            opinions = self._calcOpinions(graph, comm)
            neighbors = comm
            self.internals['nodesToAdd'].append((opinions,neighbors))
            log.debug('NewNodeRule decided to add new node with opinions ' + str(opinions)
                      + ' to community ' + str(comm))

        return self.internals

    def _getCommunities(self, graph):
        """
        Calculates the communities using the python-louvain package.
        Returns a list of lists. One list of node ids for every community.
        Nodes outside all communities are not included.
        """
        bp = community.best_partition(graph)
        comms = []
        if np.all(bp == 0):
            log.debug('found no communities')
        else:
            for nodeId in bp:
                if bp[nodeId] >= len(comms):
                    comms.append([nodeId])
                else:
                    comms[bp[nodeId]].append(nodeId)

        return comms

    def _findOperands(self, graph):
        communities = self._getCommunities(graph)
        connectedCommunities = []
        for comm in communities:
            commGraph = graph.subgraph(comm)
            isDense = nx.density(commGraph) >= self.parameters['densityThreshold']
            hasHighOrientation = np.mean([graph.edges[eid][Graph.KEY_ORIENTATION] for eid in commGraph.edges]) >= self.parameters['meanOrientationThreshold']
            if isDense and hasHighOrientation:
                connectedCommunities.append(comm)
            else:
                log.debug('Community ' + str(comm) + ' was not selected. isDense: ' + str(isDense)
                          + ', hasHighOrientation: ' + str(hasHighOrientation))

        return connectedCommunities

    def _calcOpinions(self, graph, nodeSet):
        opinionMat = np.array([graph.nodes[nid][Graph.KEY_OPINIONS] for nid in nodeSet])
        opinionMeans = np.mean(opinionMat,0) # mean op_i of all nodes
        newNodeOpinions = np.sign(opinionMeans)*np.greater(np.abs(opinionMeans),self.parameters['opMeanThreshold'])

        return list(newNodeOpinions)

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph, _parameters, _internals)

        for nodeToAdd in self.internals['nodesToAdd']:
            opinions = nodeToAdd[0]
            node = Graph.createNewNodeSkeleton(graph)
            node[Graph.KEY_OPINIONS] = opinions
            graph.add_nodes_from([(node[Graph.KEY_NODE_ID],node)])
            log.debug('Added node ' + str(graph.nodes[node[Graph.KEY_NODE_ID]]))
            for neighbour in nodeToAdd[1]:
                edge = Graph.createNewEdgeSkeleton(graph, node, graph.nodes[neighbour])
                graph.add_edges_from([(node[Graph.KEY_NODE_ID], neighbour,edge)])
                log.debug('Added edge ' + str(graph.edges[edge[Graph.KEY_EDGE_ID]]))

        return graph

    @staticmethod
    def getName():
        return 'NewNodeRule'

class NewEdgesRule(Rule):
    """
    Chooses an edge (probability weighed with orientation). Neighbours of one node can become
    neighbours of the other node also.
    createEdgeProbability: probability that an edge is created. Range: 0 to 1. Default: 0.1
    """

    defaultParameters = {'createEdgeProbability': 0.1}

    def _getNeighbours(self, graph, node, degree):
        neighbours = set()
        if degree > 0:
            for neighbour in self._getNeighbours(node, degree-1):
                neighbours.update(nx.neighbors(graph, neighbour))

    # Search for nodes that are not connected to nodeToConnect. Starts with the nodesToCheck,
    # then go on with their neighbours of increasing neighbourhood degree, until at least one
    # node is returned.
    # Return empty set if nodeToConnect is already connected with all other nodes.
    def _addUnconnected(self, graph, nodeToConnect, nodesToCheck):
        fullyConnectedCriterion = len(list(nx.neighbors(graph,nodeToConnect))) == len(list(graph.nodes))-1
        nothingToCheckCriterion = len(nodesToCheck) == 0
        if fullyConnectedCriterion or nothingToCheckCriterion:
            return []
        edgesToAdd = set()
        checkedNeighbours = set()
        for nodeToCheck in nodesToCheck:
            checkedNeighbours.update(nx.neighbors(graph,nodeToCheck))
            edgesToAdd.update([(nodeToConnect, neighbour) for neighbour in checkedNeighbours if not (graph.has_edge(neighbour,nodeToConnect) or neighbour==nodeToConnect)])
        if len(edgesToAdd) == 0:
            edgesToAdd = self._addUnconnected(graph, nodeToConnect, checkedNeighbours)

        return edgesToAdd


    def _createInternals(self, graph):
        self.internals = {'edgeId': self._findOperands(graph)
                              }

        if self.internals['edgeId'] is not None:
            nodeToConnect = self.internals['edgeId'][0]
            fixedNode = self.internals['edgeId'][1]
            edgeCandidates = self._addUnconnected(graph, nodeToConnect, [fixedNode])
            edgesToAdd = set()
            for edgeCandidate in edgeCandidates:
                if random.random() < self.parameters['createEdgeProbability']:
                    edgesToAdd.add(edgeCandidate)
            self.internals['newEdges'] = list(edgesToAdd)

        return self.internals

    def _findOperands(self, graph):
        return selectEdgeFromGraph(graph, weight_getter=lambda edge : abs(graph.edges[edge][Graph.KEY_ORIENTATION]))

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph, _parameters, _internals)
        log.debug('NewEdgeRule add edges ' + str(self.internals['newEdges']))
        if self.internals['newEdges'] is not None:
            for edgeToAdd in self.internals['newEdges']:
                edge = Graph.createNewEdgeSkeleton(graph, graph.nodes[edgeToAdd[0]], graph.nodes[edgeToAdd[1]])
                graph.add_edges_from([(edgeToAdd[0],edgeToAdd[1],edge)])

        return graph

    @staticmethod
    def getName():
        return 'NewEdgesRule'

class RemoveEdgeRule(Rule):
    """
    Chooses an edge with low orientation and removes it.

    absOrientationThreshold: maximum absolute orientation to perform edge removal. Range: 0 to 1. Default: 0.1
    """
    defaultParameters = {'absOrientationThreshold': 0.1}

    def _createInternals(self, graph):
        self.internals = {'edgeId': self._findOperands(graph)
                          }

        return self.internals

    def _findOperands(self, graph):
        try:
            return selectEdgeFromGraph(graph,predicate=lambda edgeId: abs(graph.edges[edgeId][Graph.KEY_ORIENTATION]) < self.parameters['absOrientationThreshold'])
        except(TimeoutError):
            log.debug('Found no edge with low orientation')

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph, _parameters, _internals)

        edgeId = self.internals['edgeId']
        if edgeId is not None:
            log.debug('Removing edge ' + str(edgeId) + ' with low orientation')
            graph.remove_edges_from([edgeId])

        return graph

    @staticmethod
    def getName():
        return 'RemoveEdgeRule'

class TakeoverRule(Rule):
    """
    removalProbability: probability that a suitable edge is removed. Range: 0 to 1. Default: 0.5
    minDifference: minimum difference in V of the two nodes that this rule can be applied to them.
    """

    defaultParameters = {'removalProbability': 0.5,
                         'minDifference': 1,
                         }

    def _createInternals(self, graph):
        self.internals = {'edgeId': self._findOperands(graph),
                          'edgesToRemove': [],
                          }

        if self.internals['edgeId'] is not None:
            commonNeighbours = [candidate for candidate in nx.neighbors(graph,self.internals['edgeId'][0]) if candidate in nx.neighbors(graph,self.internals['edgeId'][1])]
            weakerNodeId = self.internals['edgeId'][0 if graph.nodes[self.internals['edgeId'][0]][Graph.KEY_V] < graph.nodes[self.internals['edgeId'][1]][Graph.KEY_V] else 1]

            for commonNeighbour in commonNeighbours:
                if self._calcVDiffMetrik(graph.nodes[self.internals['edgeId'][0]][Graph.KEY_V],graph.nodes[self.internals['edgeId'][1]][Graph.KEY_V]) >= self.parameters['minDifference'] and random.random() < self.parameters['removalProbability']:
                    self.internals['edgesToRemove'].append((weakerNodeId, commonNeighbour))

        return self.internals

    def _calcVDiffMetrik(self, v1, v2):
        return abs(v1-v2)

    def _findOperands(self, graph):
        return selectEdgeFromGraph(graph, weight_getter=lambda edgeId:self._calcVDiffMetrik(graph.nodes[edgeId[0]][Graph.KEY_V],graph.nodes[edgeId[1]][Graph.KEY_V]))

    def apply(self, graph, _parameters=None, _internals=None):
        self._prepareApply(graph,_parameters, _internals)

        if self.internals['edgeId'] is not None:
            log.debug('Removing edges ' + str(self.internals['edgesToRemove']) + ' because one node of ' + str(self.internals['edgeId']) + ' is stronger')
            graph.remove_edges_from(self.internals['edgesToRemove'])

        return graph

    @staticmethod
    def getName():
        return 'TakeoverRule'
