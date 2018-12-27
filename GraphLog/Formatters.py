import GraphLog as gl
import json
import Graph

class GraphLogJsonFormatter:
    @staticmethod
    def formatEntry(entry):
        if isinstance(entry, gl.GraphLogRuleEntry):
            jsonStr = json.dumps({
                'type':'GraphLogRuleEntry',
                'rulename':entry.rulename,
                'parameters':entry.parameters,
                'internals':entry.internals
                })
            return jsonStr
        if isinstance(entry, gl.GraphLogSnapshotEntry):
            jsonStr = json.dumps({
                'type':'GraphLogSnapshotEntry',
                'version':Graph.getVersion(entry.graph),
                'graph':Graph.toJsonStr(entry.graph)
                })
            return jsonStr

    @staticmethod
    def parseEntry(jsonStr):
        jsonDict = json.loads(jsonStr)
        if jsonDict['type'] == 'GraphLogRuleEntry':
            return gl.GraphLogRuleEntry(jsonDict['rulename'], jsonDict['parameters'], jsonDict['internals'])
        elif jsonDict['type'] == 'GraphLogSnapshotEntry':
            g = Graph.fromJsonStr(jsonDict['graph'])
            Graph.setVersion(g, jsonDict['version'])
            return gl.GraphLogSnapshotEntry(g)
