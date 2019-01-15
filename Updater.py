from Rules import *
import Graph
import random
import GraphLog as gl
from utils.Logger import get_graph_logger
import Analyser

class Updater:
    default_config = {
        'logging_enabled': False,
        'OrientationConfirmationRule_weight': 1,
        'AdaptationRule_weight': 1,
        'NewNodeRule_weight': 1,
        'NewEdgesRule_weight': 1,
        'RemoveEdgeRule_weight': 1,
        'TakeoverRule_weight': 1,
    }

    def __init__(self, ruleset=None, config=default_config):
        if ruleset is None:
            ruleset = getRuleset()
        self.rules = {rulename:{'rule':rule,'weight':config[rulename+'_weight']} for rulename, rule in ruleset.items()}
        self.analyzer = Analyser.Analyser()
        self.writeLog = config['logging_enabled']

    def setGraph(self, graph, logger):
        self.graph = graph
        self.graph = Graph.calculateAttributes(self.graph)

        if self.writeLog:
            self.graphLogger = gl.GraphLogger(self.graph, gl.GraphLogWriter(logger))
            self.graphLogger.setGraphGetter(lambda : self.graph)

        self.analyzer.initAnalysis(self.graph, config={'stepSize':10})
        self.analyzer.onNewVersion(self.graph)

    def update(self, ruleName = None):
        self.applyRule(ruleName)

    def applyRule(self, ruleName=None):
        if ruleName is None:
            ruleName = random.choices(list(self.rules), [rule['weight'] for rule in self.rules.values()],k=1)[0]

        # TODO: get rule's requirements and choose items
        # for the rule to operate on
        try:
            self.graph = self.rules[ruleName]['rule'].apply(self.graph)

            self.graph = Graph.calculateAttributes(self.graph)

            Graph.incrementVersion(self.graph)

            if self.writeLog:
                self.graphLogger.logRule(self.rules[ruleName]['rule'])

            self.analyzer.onNewVersion(self.graph)
        except TimeoutError:
            pass

    def close(self):
        if self.writeLog:
            self.graphLogger.close()
        self.analyzer.finishAnalysis(self.graph)

    def getAnalyzer(self):
        return self.analyzer
