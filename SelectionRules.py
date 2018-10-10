import random

# Anforderung an node: ID muss enthalten sein
KEY_NODE_ID = 'id'

def selectItemFromSet(set, weight_getter, predicate, maxChoiceTries):
    weights = []
    for item in set:
        weights.append(weight_getter(item))
    
    chosenItem = None
    tryCtr = 0
    while not chosenItem:
        if tryCtr >= maxChoiceTries:
            raise TimeoutError("Choice try limits exceeded. Maybe a problem with the predicate?")
        
        itemCandidate = random.choices(set, weights,k=1)[0]
        if predicate(itemCandidate):
            chosenItem = itemCandidate
        
        tryCtr += 1

    return chosenItem
    
'''
Selects one random node from the graph.

The choice can be incluenced by specifying a weight_getter function and/or a predicate.
The weight_getter function takes the graph and a node as arguments and calculates the weight
for this node (scalar value). When no function is specified, all nodes have the same weight.
The predicate can be specified to ensure the chosen node fulfills some requirements. When no
function is specified, all nodes can be chosen.
If no suitable node could be found after maxChoiceTries, the function raises an error. 
'''
def selectNodeFromGraph(graph, weight_getter=lambda node:1, predicate=lambda node: True, maxChoiceTries=100):
    return selectItemFromSet(list(graph.nodes()), weight_getter, predicate, maxChoiceTries)

'''
Selects one random edge from the graph.

The choice can be incluenced by specifying a weight_getter function and/or a predicate.
The weight_getter function takes the graph and an edge as arguments and calculates the weight
for this edge (scalar value). When no function is specified, all edges have the same weight.
The predicate can be specified to ensure the chosen edge fulfills some requirements. When no
function is specified, all edges can be chosen.
If no suitable edge could be found after maxChoiceTries, the function raises an error. 
'''
def selectEdgeFromGraph(graph, weight_getter=lambda edge:1, predicate=lambda edge: True, maxChoiceTries=100):
    return selectItemFromSet(list(graph.edges()), weight_getter, predicate, maxChoiceTries)