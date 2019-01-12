from Rules import *
import Graph
import random
import GraphLog as gl
from utils.Logger import get_graph_logger
import Analyser

class Updater:
    def __init__(self, ruleset=None):
        if ruleset is None:
            ruleset = getRuleset()
        self.rules = ruleset
        self.analyzer = Analyser.Analyser()

    def setGraph(self, graph, logger):
        self.graph = graph
        self.graph = Graph.calculateAttributes(self.graph)

        self.graphLogger = gl.GraphLogger(self.graph, gl.GraphLogWriter(logger))
        self.graphLogger.setGraphGetter(lambda : self.graph)

        self.analyzer.initAnalysis(self.graph, config={'stepSize':10})
        self.analyzer.onNewVersion(self.graph)

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

            Graph.incrementVersion(self.graph)

            self.graphLogger.logRule(self.rules[ruleName])

            self.analyzer.onNewVersion(self.graph)
        except TimeoutError:
            pass

    def close(self):
        self.graphLogger.close()
        self.analyzer.finishAnalysis(self.graph)

    def getAnalyzer(self):
        return self.analyzer
