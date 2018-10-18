from Rules import *
from Graph import calculateAttributes
import random

class Updater:
    def __init__(self):
        self.rules = {}
        #self.rules[OrientationConfirmationRule.getName()] = OrientationConfirmationRule()
        self.rules[AdaptationRule.getName()] = AdaptationRule()


    def setGraph(self, graph):
        self.graph = graph
        self.graph = calculateAttributes(self.graph)

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
        self.graph = self.rules[ruleName].apply()
        # TODO: log rule application
