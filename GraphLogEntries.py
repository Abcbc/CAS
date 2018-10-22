class GraphLogRuleEntry:
    def __init__(self, rulename, parameters, internals):
        self.rulename = rulename
        self.parameters = parameters
        self.internals = internals

class GraphLogSnapshotEntry:
    def __init__(self, graph):
        self.graph = graph
