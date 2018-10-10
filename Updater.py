class Updater:
    rules = []
    
    def __init__(self):
        pass#rules.append()
    
    def setGraph(self, graph):
        self.graph = graph
    
#     def addRule(self, rule):
#         self.rules.append(rule)
    
    def update(self):
        for rule in self.rules:
            print(rule)        