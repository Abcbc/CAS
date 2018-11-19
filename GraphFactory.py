import copy
import networkx as nx
import random

class Graph_factory:


    '''
    assigns opinions to graphs nodes, adhering to given likelihoods
    '''

    @classmethod
    def apply_opinions(cls, graph, pro_likelihood, con_likelihood):
        if graph is None:
            return None
        for i in range(nx.number_of_nodes(graph)):
            rand = random.uniform(0, 1)
            if rand <= pro_likelihood:
                graph.node[0]['opinion'] = 1
            elif rand >= 1-con_likelihood:
                graph.node[0]['opinion'] = -1
            else:
                graph.node[0]['opinion'] = 0
        return graph


    '''
    inserts edges between given graphs to create connected graph
    '''

    @classmethod
    def connect_clusters(cls, graphs):
        cpy = copy.deepcopy(graphs)
        if graphs is None or len(graphs) == 0:
            return None

        result_graph = cpy.pop()
        while len(cpy) > 0:
            rand = random.randint(0, len(cpy)-1)    #select subgraph to add
            subgraph = cpy.pop(rand)
            offset_to_new_nodes = nx.number_of_nodes(result_graph)
            subgraph_number_of_nodes = nx.number_of_nodes(subgraph)
            result_graph = nx.disjoint_union(result_graph, subgraph)
            #connect by random edge connected to graph
            node_idx_1 = random.randint(0, offset_to_new_nodes - 1)
            node_idx_2 = offset_to_new_nodes + random.randint(0, subgraph_number_of_nodes - 1)
            result_graph.add_edge(node_idx_1, node_idx_2)
        return result_graph


    '''
    creates creates initialised connected clusters
    '''

    @staticmethod
    def buildRandomConnectedClusters(type, numberOfClusters, numberOfNodesEach, numberOfInitialConnections, probability, pro_likelihood=0.3, con_likelihood=0.2, numberOfAttempts=100):
        resultGraph = None
        subgraphs = []
        i = 0

        while i < numberOfClusters:
            subgraph = None
            if type == "Barabasi-Albert":
                subgraph = nx.generators.barabasi_albert_graph(numberOfNodesEach, numberOfInitialConnections, seed = None)
            elif type == "Watts-Strogatz":
                subgraphs.append(nx.generators.connected_watts_strogatz_graph(numberOfNodesEach, numberOfInitialConnections, probability, numberOfAttempts, seed = None))
            elif type == "Powerlaw-Cluster":
                subgraphs.append(nx.powerlaw_cluster_graph(numberOfNodesEach, numberOfInitialConnections, probability, seed = None))
            else:
                subgraphs.append(nx.generators.complete_graph(numberOfNodesEach))

            subgraph = nx.generators.barabasi_albert_graph(numberOfNodesEach, numberOfInitialConnections, seed=None)
            subgraphs.append(subgraph)
            i += 1

            Graph_factory.apply_opinions(resultGraph, pro_likelihood, con_likelihood)
        resultGraph = Graph_factory.connect_clusters(subgraphs)
        return resultGraph



    @classmethod
    def buildWattsStrogatzGraph(g=None):
        if g is None:
            g = nx.generators.connected_watts_strogatz_graph(20, 5, 0.5, 100, seed=None)
        return g

    @classmethod
    def buildPowerlawClusterGraph(g=None):
        if g is None:
            g = nx.powerlaw_cluster_graph(20, 5, 0.7, seed=None)
        return g

    @classmethod
    def buildBarabasiAlbertGraph(g=None):
        if g is None:
            n = 20
            m = 3
            g = nx.generators.barabasi_albert_graph(n, m, seed=None)
        return g


    '''
    Creates random clusters connected to each other
    '''
    @classmethod
    def buildCompositeGraph(g=None):
        if g is None:
            g1 = Graph_factory.buildBarabasiAlbertGraph()
            nrG1nodes = g1.number_of_nodes()
            g2 = Graph_factory.buildWattsStrogatzGraph()
            nrG2Nodes = g2.number_of_nodes()

            g = nx.disjoint_union(g1, g2)

            g1Idx = random.randint(0, nrG1nodes - 1)
            g2Idx = (nrG1nodes - 1) + random.randint(0, nrG2Nodes - 1)
            g.add_edge(g1Idx, g2Idx)
        return g