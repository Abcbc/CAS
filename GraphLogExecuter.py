from Rules import getRuleset
from GraphLogger import GraphLogger
from GraphLogWriters import GraphLoggerJson

class GraphLogExecuter:
    def __init__(self, graphLogReader):
        self.graphLogReader = graphLogReader
        if not self.graphLogReader.hasSnapshotEntry():
            raise RuntimeError('Log must start with a complete graph snapshot')

        self.graph = self.graphLogReader.getSnapshotEntry().graph
        self.rules = getRuleset()

        self.graphLogger = GraphLogger(self.graph, GraphLoggerJson(filename='reproduced_log.txt'))
        self.graphLogger.setGraphGetter(lambda : self.graph)

    def getGraph(self):
        self.graph

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
            self.rules[log.rulename].setParameters(log.parameters)
            self.graph = self.rules[log.rulename].apply(self.graph,log.operands)

            self.graphLogger.logRule(self.rules[log.rulename], log.operands)

    def performStep(self):
        self.performSteps(1)
