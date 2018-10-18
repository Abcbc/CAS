from Rules import *
from Graph import calculateAttributes
import random

class Updater:
    def __init__(self):
        self.rules = []
        #self.rules.append(OrientationConfirmationRule())
        self.rules.append(AdaptationRule())
        
    
    def setGraph(self, graph):
        self.graph = graph
        self.graph = calculateAttributes(self.graph)
    
    def addRule(self, rule):
         self.rules.append(rule)
    
    def update(self):
         rule = random.choice(self.rules)
         
         rule.apply(self.graph)
         
         self.graph = calculateAttributes(self.graph)