import random
from Graph import KEY_OPINIONS, KEY_EDGE_ID, findPaths

def selectItemFromSet(set, weight_getter, predicate):
    filtered_set = [item for item in set if predicate(item)]
    if len(filtered_set) == 0:
        return None

    weights = []
    for item in filtered_set:
        weights.append(weight_getter(item))

    if all(weight == 0 for weight in weights): # probability 0 for all elements is invalid
        weights = list(map(lambda val:1, weights))
    
    chosenItem = random.choices(filtered_set, weights,k=1)[0]

    return chosenItem
    
def selectNodeFromGraph(graph, weight_getter=lambda node:1, predicate=lambda node: True):
    """
    Selects one random node from the graph.

    The choice can be influenced by specifying a weight_getter function and/or a predicate.
    The weight_getter function takes a node as arguments and calculates the weight
    for this node (scalar value). When no function is specified, all nodes have the same weight.
    The predicate can be specified to ensure the chosen node fulfills some requirements. When no
    function is specified, all nodes can be chosen.
    Returns the node id.
    If no suitable node could be found after maxChoiceTries, the function raises an error.
    """
    return selectItemFromSet(list(graph.nodes()), weight_getter, predicate)

def selectEdgeFromGraph(graph, weight_getter=lambda edge:1, predicate=lambda edge: True):
    """
    Selects one random edge from the graph.

    The choice can be influenced by specifying a weight_getter function and/or a predicate.
    The weight_getter function takes an edge as arguments and calculates the weight
    for this edge (scalar value). When no function is specified, all edges have the same weight.
    The predicate can be specified to ensure the chosen edge fulfills some requirements. When no
    function is specified, all edges can be chosen.
    Returns the edge id.
    If no suitable edge could be found after maxChoiceTries, the function raises an error.
    """
    return selectItemFromSet(list(graph.edges()), weight_getter, predicate)

#def selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge:1, weight_getter_opinion=lambda opA,opB:1, predicate=lambda edge,opA,opB:True, maxChoiceTries=100):
def selectOpinionPairFromGraph(graph, weight_getter_edge=lambda edge:1, weight_getter_opinion=None, predicate=lambda pair:True):
    """
    Selects one pair of opinions (opinions of two connected nodes about the same "subject" from the
    graph.
    NOTE: weights for opinion pairs are not supported!

    The choice can be influenced by specifying a weight_getter function for edge and opinion and/or a
    predicate.
    The weight_getter_edge function takes an edge as arguments and calculates the weight
    for this edge (scalar value). When no function is specified, all edges have the same weight.
    The weight_getter_opinion function takes two opinions and calculates the weight for this pair
    (scalar value). When no function is specified, all pairs have the same weight.
    The predicate can be specified to ensure the chosen edge fulfills some requirements. When no
    function is specified, all edges can be chosen.
    Returns a dictionary with 'edge' (the edge dictionary) and 'opinionIndex' (the index of the chosen
    opinion pair.
    If no suitable edge could be found after maxChoiceTries, the function raises an error.
    """
    if weight_getter_opinion is not None:    
        raise NotImplementedError("weight getter for opinions is not supported yet")
     
    pairs = []
    for edgeId in graph.edges:
        for idx in range(len(graph.nodes[edgeId[0]][KEY_OPINIONS])):
            pairs.append({'edge':graph.edges[edgeId], 'opinionIndex':idx})

    pairWithEdgeObjects = selectItemFromSet(pairs, weight_getter=lambda pair:weight_getter_edge(pair['edge']), predicate=predicate)
    return {'edgeId':pairWithEdgeObjects['edge'][KEY_EDGE_ID], 'opinionIndex':pairWithEdgeObjects['opinionIndex']} if pairWithEdgeObjects is not None else None

def selectPathFromGraph(graph, len, weight_getter=lambda path:1, predicate=lambda path:True):
    """
    Selects one path with 'len' edges from the graph. The first and the last node in the path will not be the same.

    The choice can be influenced by specifying a weight_getter function and/or a predicate.
    The weight_getter function takes a list of nodes (the path) as arguments and calculates
    the weight for this path (scalar value). When no function is specified, all paths have the same weight.
    The predicate can be specified to ensure the chosen path fulfills some requirements. When no
    function is specified, all paths can be chosen.
    Returns the path as a list of edges.
    If no suitable path could be found after maxChoiceTries, the function raises an error.
    """
    paths = []
    for n in graph.nodes:
        paths.extend(findPaths(graph, len, n))


    return selectItemFromSet(paths, weight_getter, predicate)
