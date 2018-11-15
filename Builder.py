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

def buildTestGraphForNewEdgeRule(degreeToSearch=1):
    g = nx.Graph()

    if degreeToSearch == 0: # special case: all connected
        g = nx.complete_graph(3)
    elif degreeToSearch == 1:
        g.add_edge(0,1)
        g.add_edge(1,2)
        g.add_edge(1,3)
    elif degreeToSearch == 2:
        g.add_edge(0,1)
        g.add_edge(0,2)
        g.add_edge(1,2)
        g.add_edge(2,3)
    elif degreeToSearch == 3:
        g.add_edge(0,1)
        g.add_edge(0,2)
        g.add_edge(0,3)
        g.add_edge(1,2)
        g.add_edge(2,3)
        g.add_edge(3,4)
    else:
        raise NotImplementedError('degreeToSearch to high (between 0 and 3)')

    return buildGraph(g)
