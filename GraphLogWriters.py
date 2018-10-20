import json
from GraphLogEntries import GraphLogRuleEntry, GraphLogSnapshotEntry
from Graph import toJsonStr, fromJsonStr

# TODO: write to and parse from JSON in the classes themselves
class GraphLogJsonFormatter:
    @staticmethod
    def formatEntry(entry):
        if isinstance(entry, GraphLogRuleEntry):
            jsonStr = json.dumps({
                'type':'GraphLogRuleEntry',
                'rulename':entry.rulename,
                'parameters':entry.parameters,
                'operands':entry.operands
                })
            return jsonStr
        if isinstance(entry, GraphLogSnapshotEntry):
            jsonStr = json.dumps({
                'type':'GraphLogSnapshotEntry',
                'graph':toJsonStr(entry.graph)
                })
            return jsonStr

    @staticmethod
    def parseEntry(jsonStr):
        json = json.loads(jsonStr)
        if json['type'] == 'GraphLogRuleEntry':
            return GraphLogRuleEntry(json['rulename'], json['parameters'], json['operands'])
        elif json['type'] == 'GraphLogSnapshotEntry':
            return GraphLogSnapshotEntry(fromJsonStr(json['graph']))

class GraphLoggerJson:
    def __init__(self, doPrint=False, filename=None):
        self.doPrint = doPrint
        self.file = None
        if filename is not None:
            self.file = open(filename,'w')

    def writeEntry(self, entry):
        strEntry = GraphLogJsonFormatter.formatEntry(entry)
        if self.doPrint:
            print(strEntry)
        if self.file is not None:
            self.file.write(strEntry + '\n')
