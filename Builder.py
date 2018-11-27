import networkx as nx
import random
from Graph import addConvenienceAttributes, KEY_OPINIONS, KEY_VERSION

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
    g.graph[KEY_VERSION] = 0
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

def buildTestGraphForTakeoverRule():
    g = nx.Graph()

    # we need two connected nodes, one with high V, one with low V
    # => one should have few neighbours with orientation near zero (node 0)
    # => the other many neighbours with high orientation (pos or neg) (node 1)
    # they have a common neighbour (node 7). Connection (0,8) should be removed.

    g.add_edges_from([(0,1)])
    g.add_edges_from([(0,2)])
    g.add_edges_from([(1,3),(1,4),(1,5),(1,6),(3,4),(3,5),(3,6),(4,5),(4,6),(5,6)])
    g.add_edges_from([(0,7),(1,7)])

    g = buildGraph(g)

    g.nodes[0][KEY_OPINIONS] = [1,-1,0,0]
    g.nodes[2][KEY_OPINIONS] = [0,0,1,-1]

    g.nodes[1][KEY_OPINIONS] = [1,-1,1,-1]
    g.nodes[3][KEY_OPINIONS] = [1,-1,1,-1]
    g.nodes[4][KEY_OPINIONS] = [1,-1,1,-1]
    g.nodes[5][KEY_OPINIONS] = [-1,1,-1,1]
    g.nodes[6][KEY_OPINIONS] = [-1,1,-1,1]

    g.nodes[7][KEY_OPINIONS] = [0,0,0,0]

    return g;
