import GraphLog as gl

class GraphLogReader:
    def __init__(self, filename, formatter=gl.GraphLogJsonFormatter):
        self.formatter = formatter
        self.file = open(filename,'r')
        self.parseNext()

    def hasEntry(self):
        return self.nextToken != None

    def hasRuleEntry(self):
        return self.hasEntry() and isinstance(self.nextToken, gl.GraphLogRuleEntry)

    def hasSnapshotEntry(self):
        return self.hasEntry() and isinstance(self.nextToken, gl.GraphLogSnapshotEntry)

    def parseNext(self):
        nextLine = self.file.readline()
        if nextLine != '': # EOF
            self.nextToken = self.formatter.parseEntry(nextLine)
        else:
            self.nextToken = None

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
