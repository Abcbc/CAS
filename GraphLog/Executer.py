from Rules import getRuleset
import GraphLog as gl
from Graph import calculateAttributes, incrementVersion
from utils.Logger import get_graph_logger
import Analyser

class GraphLogExecuter:
    def __init__(self, graphLogReader):
        self.graphLogReader = graphLogReader
        if not self.graphLogReader.hasSnapshotEntry():
            raise RuntimeError('Log must start with a complete graph snapshot')

        self.graph = self.graphLogReader.getSnapshotEntry().graph
        self.rules = getRuleset()

        self.graphLogger = gl.GraphLogger(self.graph, gl.GraphLogWriter(get_graph_logger('GraphLogger', 'graphReproduced.log')))
        self.graphLogger.setGraphGetter(lambda : self.graph)

        self.analyzer = Analyser.Analyser()
        self.analyzer.initAnalysis(self.graph, config={'stepSize':10})

    def getGraph(self):
        return self.graph

    def performSteps(self, n=1):
        # TODO: implement shortcut using graph snapshots
        stepsPerformed = 0
        while stepsPerformed < n and self.graphLogReader.hasEntry():
            if self.graphLogReader.hasSnapshotEntry():
                self.graphLogReader.getSnapshotEntry() # throw away
                continue

            if not self.graphLogReader.hasRuleEntry():
                raise RuntimeError('Unknown entry. Entry, but not snapshotentry should be ruleentry, but isnt')
            log = self.graphLogReader.getRuleEntry()
            self.graph = self.rules[log.rulename].apply(self.graph,log.parameters,log.internals)
            self.graph = calculateAttributes(self.graph)

            incrementVersion(self.graph)

            self.graphLogger.logRule(self.rules[log.rulename])

            self.analyzer.onNewVersion(self.graph)

    def performStep(self):
        self.performSteps(1)

    def performFullSimulation(self):
        while self.graphLogReader.hasEntry():
            self.performSteps(1)

    def getAnalyzer(self):
        return self.analyzer
