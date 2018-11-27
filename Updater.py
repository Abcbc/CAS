from Rules import *
import Graph
import random
import GraphLog as gl
from utils.Logger import get_graph_logger

class Updater:
    def __init__(self):
        self.rules = getRuleset()

    def setGraph(self, graph):
        self.graph = graph
        self.graph = Graph.calculateAttributes(self.graph)

        self.graphLogger = gl.GraphLogger(self.graph, gl.GraphLogWriter(get_graph_logger('GraphLogger', 'graph.log')))
        self.graphLogger.setGraphGetter(lambda : self.graph)

    def addRule(self, rule):
        self.rules[rule.getName()] = rule

    def update(self, ruleName = None):
        self.applyRule(ruleName)

    def applyRule(self, ruleName=None):
        if ruleName is None:
            ruleName = random.choice(list(self.rules))

        # TODO: get rule's requirements and choose items
        # for the rule to operate on
        try:
            self.graph = self.rules[ruleName].apply(self.graph)

            self.graph = Graph.calculateAttributes(self.graph)

            self.graph.graph[Graph.KEY_VERSION] += 1

            self.graphLogger.logRule(self.rules[ruleName])
        except TimeoutError:
            pass

    def close(self):
        self.graphLogger.close()
