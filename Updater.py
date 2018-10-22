from Rules import *
from Graph import calculateAttributes
import random
from GraphLogger import GraphLogger
from GraphLogWriters import GraphLoggerJson
from utils.Logger import get_graph_logger

class Updater:
    def __init__(self):
        self.rules = getRuleset()

    def setGraph(self, graph):
        self.graph = graph
        self.graph = calculateAttributes(self.graph)

        self.graphLogger = GraphLogger(self.graph, GraphLoggerJson(get_graph_logger('GraphLogger','graph.log')))
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

            self.graph = calculateAttributes(self.graph)

            self.graphLogger.logRule(self.rules[ruleName])
        except TimeoutError:
            pass

    def close(self):
        self.graphLogger.close()
