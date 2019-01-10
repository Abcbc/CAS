import copy
import networkx as nx
import random
from Graph import KEY_OPINIONS, calculateAttributes, addConvenienceAttributes, setVersion
import generators.actors as act

NUMBER_OF_KEY_OPINIONS = 4
LIST_OF_CONSENSE_INDEXES = [0, 2]
DEFAULT_NUMBER_OF_ATTEMPTS = 100




class GraphFactory:
    """
    Verteilungs methoden.
    """

    def __init__(self, sim_settings):
        self.graph_type = sim_settings['graph_type']
        self.branch_probability = sim_settings["graph_branch_probability"]
        self.num_of_nodes = sim_settings["graph_num_of_node"]
        self.num_of_cluster = sim_settings["graph_cluster"]
        self.opinion_factory = act.OpinionFactory(sim_settings)
        self.initial_connections = sim_settings["graph_init_connects"]
        self.node_distribution_method = self.node_distribution_mapper(sim_settings["graph_cluster_distribution"])
        self.actor_init_method = self.actor_method_mapper(sim_settings["actor_method"])

    def _even(self, cluster):
        result = [0 for x in range(cluster)]
        for i in range(self.num_of_nodes):
            idx = self.num_of_nodes%cluster
            result[idx] += 1
        return result


    def _linear(self, cluster):
        return

    def _exponential(self, cluster):
        return

    def node_distribution_mapper(self, methode):
        cluster_distribution_mapper = {
            "even": self._even,
            "linear": self._linear,
            "_exponential": self._exponential
        }

        return cluster_distribution_mapper[methode]


    """
    Actor Methods
    """


    def _random(self, cluster):
        nodes = cluster.node

        for node in nodes:
            nodes[node][KEY_OPINIONS] = self.opinion_factory.random_create()[KEY_OPINIONS]

        return cluster

    def _deviation(self, cluster):
        for node in cluster.node:
            cluster[node][KEY_OPINIONS] = self.opinion_factory.random_create()[KEY_OPINIONS]
        return cluster

    def actor_method_mapper(self, method):
        actor_method_mapper = {
            "random": self._random,
            "deviation": self._deviation
        }

        return actor_method_mapper[method]

    def _create_cluster(self, type, num_of_nodes, initial_connections, probability):
        #TODO: Return 1 cluster

        if type == 'default':
            subgraph = nx.generators.barabasi_albert_graph(num_of_nodes, initial_connections, seed=None)
        elif type == 'Barabasi-Albert':
            subgraph = nx.generators.barabasi_albert_graph(num_of_nodes, initial_connections, seed=None)
        elif type == 'Watts-Strogatz':
            subgraph = nx.generators.connected_watts_strogatz_graph(num_of_nodes, initial_connections, probability, seed = None)
        elif type == "Powerlaw-Cluster":
                subgraph = nx.powerlaw_cluster_graph(num_of_nodes, initial_connections, probability, seed = None)
        elif type == 'complete':
            subgraph = nx.generators.complete_graph(num_of_nodes)


        subgraph = self.actor_init_method(subgraph)

        return subgraph


    def _connected(self, clusters, connection=1):

        result = self.connect_clusters_n_times(clusters, connection)
        return result

    def create(self):

        node_distrebution = self.node_distribution_method(self.num_of_cluster)
        clusters = []

        for nodes in node_distrebution:

            cluster = self._create_cluster(type=self.graph_type, num_of_nodes=self.num_of_nodes, initial_connections=self.initial_connections,
                                                   probability=self.branch_probability)

            clusters.append(cluster)

        g = self._connected(clusters,self.initial_connections)
        setVersion(g,0)
        return addConvenienceAttributes(calculateAttributes(g))




    @staticmethod
    def get_default_setup():
        graph = GraphFactory.buildConnectedClustersToSpec(GraphFactory.get_default_settings())
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
    def get_merging_graphs_settings(cluster_a_size, cluster_b_size):
        cluster0 = {'type': "complete", 'number_of_nodes': cluster_a_size, 'initial_connections': 0, 'probability':0.0, 'pro_likelihood': 1.0, 'con_likelihood': 0.0, 'consense_indexes': [0, 1, 2, 3]}
        cluster1 = {'type': "complete", 'number_of_nodes': cluster_b_size, 'initial_connections': 0, 'probability': 0.0, 'pro_likelihood': 1.0, 'con_likelihood': 0.0, 'consense_indexes': [0, 1, 2, 3]}
        cluster_list = [cluster0, cluster1]
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
    def apply_alternating_opinions(graph, index_list):
        """
        assigns alternating values to graph's opinion indexes in given list
        """
        for opinion_index in range(len(index_list)):
            index_list[opinion_index] = opinion_index % NUMBER_OF_KEY_OPINIONS

        if graph is None:
            return None

        i = 0;
        for nodeId in graph.node:
            for opinion_index in index_list:
                if i % 2 == 0:
                    graph.node[nodeId][KEY_OPINIONS][opinion_index] = 1
                else:
                    graph.node[nodeId][KEY_OPINIONS][opinion_index] = -1
            i += 1
        graph = calculateAttributes(graph)

        return graph

    @staticmethod
    def apply_opinions(graph, pro_likelihood, con_likelihood, opinion_indexes):
        """
        assigns opinions to graphs nodes, adhering to given likelihoods
        """
        if graph is None:
            return None
        graph = GraphFactory.apply_random_opinions(graph)

        for idx in opinion_indexes:
            graph = GraphFactory.apply_specific_common_opinion(graph, pro_likelihood, con_likelihood, idx)


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
    def connect_clusters_n_times(graphs, number_of_times):
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

            used_edges = [[-1, -1]]
            current_edge = [-1, -1]
            node_idx_1 = -1
            node_idx_2 = -1
            for i in range(number_of_times):
                while current_edge in used_edges:
                    node_idx_1 = random.randint(0, offset_to_new_nodes - 1)
                    node_idx_2 = offset_to_new_nodes + random.randint(0, subgraph_number_of_nodes - 1) -1
                    current_edge = [node_idx_1,node_idx_2]
                result_graph.add_edge(node_idx_1, node_idx_2)
                used_edges.append([node_idx_1, node_idx_2])

        return result_graph

    @staticmethod
    def connect_clusters_by_overlay(overlay_graph, subgraphs):
        """
        inserts subgraphs as edges between given graphs into overlay
        """
        cpy = copy.deepcopy(subgraphs)
        if subgraphs is None or len(subgraphs) == 0:
            return None

        result_graph = cpy.pop()

        number_overlay_nodes = nx.number_of_nodes(overlay_graph)
        onverlay_node_index = 0
        while len(cpy) > 0:
            rand = random.randint(0, len(cpy) - 1)  # select subgraph to add
            subgraph = cpy.pop(rand)
            offset_to_new_nodes = nx.number_of_nodes(result_graph)
            subgraph_number_of_nodes = nx.number_of_nodes(subgraph)
            result_graph = nx.disjoint_union(result_graph, subgraph)
            # connect by random edge connected to graph
            subgraph_node_idx = offset_to_new_nodes + random.randint(0, subgraph_number_of_nodes - 1)
            result_graph.add_edge(onverlay_node_index, subgraph_node_idx)
            onverlay_node_index = (onverlay_node_index + 1) % number_overlay_nodes

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
            subgraph = GraphFactory.apply_opinions(subgraph, clusterList[cluster_id]['pro_likelihood'], clusterList[cluster_id]['con_likelihood'], clusterList[cluster_id]['consense_indexes'])
            subgraphs.append(subgraph)
        resultGraph = GraphFactory.connect_clusters(subgraphs)
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

            subgraph = GraphFactory.apply_opinions(subgraph, pro_likelihood, con_likelihood, LIST_OF_CONSENSE_INDEXES)
            subgraphs.append(subgraph)
            i += 1

        resultGraph = GraphFactory.connect_clusters(subgraphs)
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
            g1 = GraphFactory.buildBarabasiAlbertGraph()
            nrG1nodes = g1.number_of_nodes()
            g2 = GraphFactory.buildWattsStrogatzGraph()
            nrG2Nodes = g2.number_of_nodes()

            g = nx.disjoint_union(g1, g2)

            g1Idx = random.randint(0, nrG1nodes - 1)
            g2Idx = (nrG1nodes - 1) + random.randint(0, nrG2Nodes - 1)
            g.add_edge(g1Idx, g2Idx)
        return g

    def _core_groups(self, cluster):
        core_dict = nx.core_number(cluster)
        result_dict = {}.fromkeys(set(core_dict.values()), [])

        for key in core_dict:
            result_dict[core_dict[key]].append(key)

        return result_dict


