from Rules import *
from Graph import calculateAttributes
import random
from GraphLogger import GraphLogger
from GraphLogWriters import GraphLoggerJson

graphLogger = None

class Updater:
    def __init__(self):
        self.rules = getRuleset()

    def setGraph(self, graph):
        self.graph = graph
        self.graph = calculateAttributes(self.graph)

        global graphLogger
        graphLogger = GraphLogger(self.graph, GraphLoggerJson(filename='log.txt'))
        graphLogger.setGraphGetter(lambda : self.graph)

    def addRule(self, rule):
        self.rules[rule.getName()] = rule

    def update(self, ruleName = None):
        self.applyRule(ruleName)

        self.graph = calculateAttributes(self.graph)

    def applyRule(self, ruleName=None):
        if ruleName is None:
            ruleName = random.choice(list(self.rules))

        # TODO: get rule's requirements and choose items
        # for the rule to operate on
        operands = self.rules[ruleName].getOperands(self.graph)
        self.graph = self.rules[ruleName].apply(self.graph, operands)

        graphLogger.logRule(self.rules[ruleName], operands)
