import json
from GraphLog import GraphLogRuleEntry, GraphLogSnapshotEntry
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
                'internals':entry.internals
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
        jsonDict = json.loads(jsonStr)
        if jsonDict['type'] == 'GraphLogRuleEntry':
            return GraphLogRuleEntry(jsonDict['rulename'], jsonDict['parameters'], jsonDict['internals'])
        elif jsonDict['type'] == 'GraphLogSnapshotEntry':
            return GraphLogSnapshotEntry(fromJsonStr(jsonDict['graph']))

class GraphLoggerJson:
    def __init__(self, logger):
        self.logger = logger

    def writeEntry(self, entry):
        strEntry = GraphLogJsonFormatter.formatEntry(entry)
        self.logger.info(strEntry)

    def close(self):
        pass #TODO flush logger
