class GraphLogRuleEntry:
    def __init__(self, rulename, parameters, operands):
        self.rulename = rulename
        self.parameters = parameters
        self.operands = operands

class GraphLogSnapshotEntry:
    def __init__(self, graph):
        self.graph = graph