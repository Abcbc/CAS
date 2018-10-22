from GraphLogEntries import GraphLogRuleEntry, GraphLogSnapshotEntry

class GraphLogger:
    def __init__(self, startGraph, graphLogWriter):
        self.log = []
        self.graphLogWriter = graphLogWriter
        self.graphGetter = None

        self._logEntryId = 0
        self.ruleCnt = 0
        self.snapshotDistance = 10
        self.snapshotIds = []

        # log first graph
        self.log.append((self._getLogEntryId(),GraphLogSnapshotEntry(startGraph)))
        self.graphLogWriter.writeEntry(self.log[-1][1])

    def _getLogEntryId(self):
        self._logEntryId += 1
        return self._logEntryId

    def setGraphGetter(self,graphGetter):
        self.graphGetter = graphGetter

    # arguments are subject to change, just written to get a first impression
    def logRule(self, rule):
        self.log.append((self._getLogEntryId(),GraphLogRuleEntry(rule.getName(), rule.getParameters(), rule.getOperands())))
        self.ruleCnt += 1

        self.graphLogWriter.writeEntry(self.log[-1][1])

        if self.graphGetter is not None and self.ruleCnt >= self.snapshotDistance:
            self.log.append((self._getLogEntryId(),GraphLogSnapshotEntry(self.graphGetter())))
            self.graphLogWriter.writeEntry(self.log[-1][1])
            self.ruleCnt = 0

    def close(self):
        self.graphLogWriter.close()
