import networkx as nx
import random
from Graph import addConvenienceAttributes

def getRandomOpinion():
    return random.randint(-1,1)

# use g as a base if given
def buildGraph(g=None):
    if g is None:
        g = nx.complete_graph(3)
    for nodeId in g.node:
        g.nodes()[nodeId]['opinions']=[getRandomOpinion(),getRandomOpinion(),getRandomOpinion()]
        g.nodes()[nodeId]['spectrum']=0

    for edgeId in g.edges():
        g.edges()[edgeId]['orientation']=0

    addConvenienceAttributes(g)
    return g
