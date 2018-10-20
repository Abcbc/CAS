from GraphLogEntries import GraphLogRuleEntry, GraphLogSnapshotEntry
from GraphLogWriters import GraphLogJsonFormatter

class GraphLoggerJson:
    def __init__(self, filename):
        self.file = open(filename,'r')
        self.parseNext()

    def hasRuleEntry(self):
        return isinstance(self.nextToken, GraphLogRuleEntry)

    def hasSnapshotEntry(self):
        return isinstance(self.nextToken, GraphLogSnapshotEntry)

    def parseNext(self):
        self.nextToken = GraphLogJsonFormatter.parseEntry(self.file.read())

    def getEntry(self):
        tkn = self.nextToken
        self.parseNext()
        return tkn

    def getRuleEntry(self):
        if not self.hasRuleEntry():
            raise RuntimeError('next entry is not a rule')
        return self.getEntry()

    def getSnapshotEntry(self):
        if not self.hasSnapshotEntry():
            raise RuntimeError('next entry is not a snapshot')
        return self.getEntry()
