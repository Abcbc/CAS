import copy
import networkx as nx
import random
from Graph import KEY_OPINIONS, calculateAttributes

NUMBER_OF_KEY_OPINIONS = 4
LIST_OF_CONSENSE_INDEXES = [0, 2]
DEFAULT_NUMBER_OF_ATTEMPTS = 100

class Graph_factory:

    @staticmethod
    def get_default_setup():
        graph = Graph_factory.buildConnectedClustersToSpec(Graph_factory.get_default_settings())
        return graph


    @classmethod
    def get_default_settings(cls):
        cluster0 = {'type': "Barabasi-Albert", 'number_of_nodes': 25, 'initial_connections': 3, 'probability':0.4, 'pro_likelihood': 0.7, 'con_likelihood': 0.1, 'consense_indexes': [0, 1]}
        cluster1 = {'type': "Watts-Strogatz", 'number_of_nodes': 15, 'initial_connections': 2, 'probability': 0.6, 'pro_likelihood': 0.5, 'con_likelihood': 0.3, 'consense_indexes': [1, 2]}
        cluster2 = {'type': "Powerlaw-Cluster", 'number_of_nodes': 5, 'initial_connections': 2, 'probability': 0.6, 'pro_likelihood': 0.2, 'con_likelihood': 0.1, 'consense_indexes': [3]}
        cluster3 = {'type': "Barabasi-Albert", 'number_of_nodes': 5, 'initial_connections': 2, 'probability': 0.6,
                    'pro_likelihood': 0.2, 'con_likelihood': 0.1, 'consense_indexes': [3]}
        cluster_list = [cluster0, cluster1, cluster2, cluster3]
        settings_dict = {'clusterList': cluster_list}
        return settings_dict

    @classmethod
    def apply_random_opinions(cls, graph):
        """
        assigns random opinions to all nodes
        """
        if graph is None:
            return None
        for nodeId in graph.node:
            graph.node[nodeId][KEY_OPINIONS] = [0, 0, 0, 0]
            for idx in range(NUMBER_OF_KEY_OPINIONS):
                opinion = random.randint(-1, 1)
                graph.node[nodeId][KEY_OPINIONS][idx] = opinion
        return graph


    @classmethod
    def apply_specific_common_opinion(cls, graph, pro_likelihood, con_likelihood, opinion_index):
        """
        assigns opinions to graphs nodes, adhering to given likelihoods
        """

        opinion_index = opinion_index % NUMBER_OF_KEY_OPINIONS
        if graph is None:
            return None
        for nodeId in graph.node:
            rand = random.uniform(0, 1)
            if rand <= pro_likelihood:
                graph.node[nodeId][KEY_OPINIONS][opinion_index] = 1
            elif rand >= 1 - con_likelihood:
                graph.node[nodeId][KEY_OPINIONS][opinion_index] = -1
            else:
                graph.node[nodeId][KEY_OPINIONS][opinion_index] = 0

        graph = calculateAttributes(graph)

        return graph


    @classmethod
    def apply_opinions(cls, graph, pro_likelihood, con_likelihood, opinion_indexes):
        """
        assigns opinions to graphs nodes, adhering to given likelihoods
        """
        if graph is None:
            return None
        graph = Graph_factory.apply_random_opinions(graph)

        for idx in opinion_indexes:
            graph = Graph_factory.apply_specific_common_opinion(graph, pro_likelihood, con_likelihood, idx)


        graph = calculateAttributes(graph)

        return graph




    @classmethod
    def connect_clusters(cls, graphs):
        """
        inserts edges between given graphs to create connected graph
        """
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


    @staticmethod
    def buildConnectedClustersToSpec(settings_dict):
        """
        creates creates initialised connected clusters
        """
        subgraphs = []

        clusterList = settings_dict['clusterList']
        for cluster_id in range(len(clusterList)):
            type = clusterList[cluster_id]['type']
            if type == "Barabasi-Albert":
                subgraph = nx.generators.barabasi_albert_graph(clusterList[cluster_id]['number_of_nodes'], clusterList[cluster_id]['initial_connections'], seed=None)
            elif type == "Watts-Strogatz":
                subgraph = nx.generators.connected_watts_strogatz_graph(clusterList[cluster_id]['number_of_nodes'], clusterList[cluster_id]['initial_connections'], clusterList[cluster_id]['probability'], DEFAULT_NUMBER_OF_ATTEMPTS, seed=None)
            elif type == "Powerlaw-Cluster":
                subgraph = nx.powerlaw_cluster_graph(clusterList[cluster_id]['number_of_nodes'], clusterList[cluster_id]['initial_connections'], clusterList[cluster_id]['probability'], seed=None)
            else:
                subgraph = nx.generators.complete_graph(clusterList[cluster_id]['number_of_nodes'])
            subgraph = Graph_factory.apply_opinions(subgraph, clusterList[cluster_id]['pro_likelihood'], clusterList[cluster_id]['con_likelihood'], clusterList[cluster_id]['consense_indexes'])
            subgraphs.append(subgraph)
        resultGraph = Graph_factory.connect_clusters(subgraphs)
        return resultGraph


    @staticmethod
    def buildRandomConnectedClusters(type, numberOfClusters, numberOfNodesEach, numberOfInitialConnections, probability, pro_likelihood=0.3, con_likelihood=0.2, numberOfAttempts=100):
        """
        creates creates initialised connected clusters
        """
        subgraphs = []
        i = 0

        while i < numberOfClusters:
            subgraph = None
            if type == "Barabasi-Albert":
                subgraph = nx.generators.barabasi_albert_graph(numberOfNodesEach, numberOfInitialConnections, seed = None)
            elif type == "Watts-Strogatz":
                subgraph = nx.generators.connected_watts_strogatz_graph(numberOfNodesEach, numberOfInitialConnections, probability, numberOfAttempts, seed = None)
            elif type == "Powerlaw-Cluster":
                subgraph = nx.powerlaw_cluster_graph(numberOfNodesEach, numberOfInitialConnections, probability, seed = None)
            else:
                subgraph = nx.generators.complete_graph(numberOfNodesEach)

            subgraph = Graph_factory.apply_opinions(subgraph, pro_likelihood, con_likelihood, LIST_OF_CONSENSE_INDEXES)
            subgraphs.append(subgraph)
            i += 1

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


    @classmethod
    def buildCompositeGraph(g=None):
        """
        Creates random clusters connected to each other
        """
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