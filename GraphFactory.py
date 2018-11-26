import copy
import networkx as nx
import random
from Graph import KEY_OPINIONS, calculateAttributes
from generators.nodes import Actors

NUMBER_OF_KEY_OPINIONS = 4
LIST_OF_CONSENSE_INDEXES = [0, 2]
DEFAULT_NUMBER_OF_ATTEMPTS = 100

class Graph_factory:
    """
    Verteilungs methoden.
    """
    @staticmethod
    def _even(num_of_nodes, cluster):
        result = [0 for x in range(cluster)]
        for i in range(num_of_nodes):
            idx = num_of_nodes%cluster
            result[idx] += 1
        return result

    @staticmethod
    def _linear(num_of_nodes, num_of_cluster):
        return

    @staticmethod
    def _exponential(num_of_nodes, num_of_cluster):
        return

    @staticmethod
    def _exponential(num_of_nodes, num_of_cluster):
        return

    @staticmethod
    def distrebution_mapper(methode, num_of_nodes, num_of_cluster):
        cluster_distrebution_mapper = {
            "even": Graph_factory._even,
            "linear": Graph_factory._linear,
            "_exponential": Graph_factory._exponential
        }

        return cluster_distrebution_mapper[methode](num_of_nodes, num_of_cluster)


    """
    Actor Methods
    """

    @staticmethod
    def _random(cluster, actor_complexity):
        for node in cluster:
            cluster[node][KEY_OPINIONS] = Actors.create()[KEY_OPINIONS]
        return cluster

    @staticmethod
    def actor_mapper(method, cluster, actor_complexity):
        actor_method_mapper = {
            "random": Graph_factory._random
        }

        return actor_method_mapper[method](cluster, actor_complexity)

    @staticmethod
    def _create_cluster(type, num_of_nodes, initial_connections, probability, actor_method):
        #TODO: Return 1 cluster


        subgraph = nx.generators.barabasi_albert_graph(num_of_nodes, initial_connections , seed=None)
        subgraph = Graph_factory.actor_mapper(actor_method,subgraph,1)
        return subgraph

    @staticmethod
    def _connected(clusters, connection=1):

        return clusters[0]

    @staticmethod
    def create(sim_settings):
        num_of_nodes = sim_settings["graph_num_of_node"]
        num_of_cluster = sim_settings["graph_cluster"]
        methode = sim_settings["graph_cluster_distrebution"]
        actor_method = sim_settings["actor_method"]
        node_distrebution = Graph_factory.distrebution_mapper(methode, num_of_nodes, num_of_cluster)
        clusters = []

        for nodes in node_distrebution:
            type = sim_settings["graph_type"]
            initial_connections = sim_settings["graph_init_connects"]
            probability = sim_settings["graph_branch_probability"]

            cluster = Graph_factory._create_cluster(type=type, num_of_nodes=nodes, initial_connections=initial_connections,
                                                    probability=probability, actor_method=actor_method)

            clusters.append(cluster)

            return calculateAttributes(Graph_factory._connected(clusters))




    @staticmethod
    def get_default_setup():
        graph = Graph_factory.buildConnectedClustersToSpec(Graph_factory.get_default_settings())
        return graph


    @staticmethod
    def get_default_settings():
        cluster0 = {'type': "Barabasi-Albert", 'number_of_nodes': 25, 'initial_connections': 3, 'probability':0.4, 'pro_likelihood': 0.7, 'con_likelihood': 0.1, 'consense_indexes': [0, 1]}
        cluster1 = {'type': "Watts-Strogatz", 'number_of_nodes': 15, 'initial_connections': 2, 'probability': 0.6, 'pro_likelihood': 0.5, 'con_likelihood': 0.3, 'consense_indexes': [1, 2]}
        cluster2 = {'type': "Powerlaw-Cluster", 'number_of_nodes': 5, 'initial_connections': 2, 'probability': 0.6, 'pro_likelihood': 0.2, 'con_likelihood': 0.1, 'consense_indexes': [3]}
        cluster3 = {'type': "Barabasi-Albert", 'number_of_nodes': 5, 'initial_connections': 2, 'probability': 0.6,
                    'pro_likelihood': 0.2, 'con_likelihood': 0.1, 'consense_indexes': [3]}
        cluster_list = [cluster0, cluster1, cluster2, cluster3]
        settings_dict = {'clusterList': cluster_list}
        return settings_dict

    @staticmethod
    def apply_random_opinions(graph):
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

    @staticmethod
    def apply_specific_common_opinion(graph, pro_likelihood, con_likelihood, opinion_index):
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

    @staticmethod
    def apply_opinions(graph, pro_likelihood, con_likelihood, opinion_indexes):
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

    @staticmethod
    def connect_clusters(graphs):
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

    @staticmethod
    def buildWattsStrogatzGraph(g=None):
        if g is None:
            g = nx.generators.connected_watts_strogatz_graph(20, 5, 0.5, 100, seed=None)
        return g

    @staticmethod
    def buildPowerlawClusterGraph(g=None):
        if g is None:
            g = nx.powerlaw_cluster_graph(20, 5, 0.7, seed=None)
        return g

    @staticmethod
    def buildBarabasiAlbertGraph(g=None):
        if g is None:
            n = 20
            m = 3
            g = nx.generators.barabasi_albert_graph(n, m, seed=None)
        return g

    @staticmethod
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