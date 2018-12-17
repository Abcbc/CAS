import copy
import networkx as nx
import random
from Graph import KEY_OPINIONS, calculateAttributes, addConvenienceAttributes, setVersion
import generators.actors as act

NUMBER_OF_KEY_OPINIONS = 4
LIST_OF_CONSENSE_INDEXES = [0, 2]
DEFAULT_NUMBER_OF_ATTEMPTS = 100
DEFAULT_NUMBER_OF_INTERCONNECTIONS = 5
DEFAULT_PRO_LIKELIHOOD = 0.5
DEFAULT_CON_LIKELIHOOD = 0.2
# experiment types
SETUP_TYPE_DEFAULT = "default"
SETUP_TYPE_MERGING = "merging"
SETUP_TYPE_DISSOCIATING = "dissociating"
SETUP_TYPE_OVERLAY = "overlay"
SETUP_TYPE_DIVERSE_CLUSTERS = "diverse_clusters"
SETUP_TYPE_DIVERSE_CORENESS = "coreness"
SETUP_TYPE_DETAILED = "custom"
SETUP_TYPE_DIVERSE_CLUSTERS_NEU = "neu"
# overlay network specifics
DEFAULT_OVERLAY_TYPE = "Barabasi-Albert"
DEFAULT_OVERLAY_INITIAL_CONNECTIONS = 3
DEFAULT_OVERLAY_BRANCH_PROBABIITY = 0.9
# graph specifics
GRAPH_TYPE = "type"
GRAPH_TYPE_BARABASI = "Barabasi-Albert"
GRAPH_TYPE_WATTS_STROGATZ = "Watts-Strogatz"
GRAPH_TYPE_POWERLAW = "Powerlaw-Cluster"


GRAPH_NUMBER_OF_NODES = "number_of_nodes"
GRAPH_NUMBER_OF_INITIAL_CONNECTIONS = "initial_connections"
GRAPH_PRO_LIKELIHOOD = "pro_likelihood"
GRAPH_CON_LIKELIHOOD = "con_likelihood"
GRAPH_BRANCH_PROBABILITY = "probability"
GRAPH_OPPINION_DISTRIBUTION_TYPE = "oppinion_distribution_type"
GRAPH_CONSENSE_INDEXES = "consense_indexes"
GRAPH_OPPINION_FIXED_LIST = "fixed_oppinion_list"

#oppinion_distributions
OPPINION_DISTRIBUTION_RANDOM = "random"
OPPINION_DISTRIBUTION_SPECIFIC = "detailed"
OPPINION_DISTRIBUTION_ALTERNATING = "alternating"
OPPINION_DISTRIBUTION_FIXED = "fixed"

class GraphFactory:
    """
    Verteilungs methoden.
    """

    def __init__(self, sim_settings):
        self.graph_type = sim_settings["graph_type"]
        self.branch_probability = sim_settings["graph_branch_probability"]
        self.num_of_nodes = sim_settings["graph_num_of_node"]
        self.num_of_clusters = sim_settings["graph_cluster"]
        self.opinion_factory = act.OpinionFactory(sim_settings)
        self.initial_connections = sim_settings["graph_init_connects"]
        self.node_distribution_method = self.node_distribution_mapper(sim_settings["graph_cluster_distribution"])
        self.actor_init_method = self.actor_method_mapper(sim_settings["actor_method"])
        self.setup_type = sim_settings["setup_type"]
        self.subgraph_list = sim_settings["subgraph_list"]
        self.setup_method = self.setup_type_mapper(self.setup_type)
        # missing in config
        self.number_of_interconnections = DEFAULT_NUMBER_OF_INTERCONNECTIONS
        self. pro_likelihood = DEFAULT_PRO_LIKELIHOOD
        self.con_likelihood = DEFAULT_CON_LIKELIHOOD
        self.consense_indexes = LIST_OF_CONSENSE_INDEXES
        #overlay network specifics
        self.overlay_type = DEFAULT_OVERLAY_TYPE
        self.overlay_initial_connections = DEFAULT_OVERLAY_INITIAL_CONNECTIONS
        self.overlay_branch_probability = DEFAULT_OVERLAY_BRANCH_PROBABIITY

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

    def setup_type_mapper(self, setup_type):
        """
        Maps graph construction method to name
        :param setup_type:
        :return:    method
        """
        setup_type_map = {
            SETUP_TYPE_DEFAULT: self.buildEqualConnectedClustersToSpec,
            SETUP_TYPE_MERGING: self._buildConnectedClustersToSpec,
            SETUP_TYPE_DISSOCIATING: self._build_dissociating_graph,
            SETUP_TYPE_OVERLAY: self._build_clusters_with_overlay,
            SETUP_TYPE_DIVERSE_CLUSTERS: self._buildConnectedClustersToSpecList,
            SETUP_TYPE_DIVERSE_CLUSTERS_NEU: self.neu_buildConnectedClustersToSpecList,
            SETUP_TYPE_DIVERSE_CORENESS: self._buildClustersWithCoreness,
            SETUP_TYPE_DETAILED: self._build_graphs_to_detailed_description
        }
        return setup_type_map[setup_type]

    def node_distribution_mapper(self, methode):
        cluster_distribution_mapper = {
            "even": self._even,
            "linear": self._linear,
            "exponential": self._exponential,
            "alternating": self._apply_alternating_opinions,
            "common_opinions": self._apply_specific_common_opinion
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

    # def _create_cluster(self, type, num_of_nodes, initial_connections, probability):
    #     #TODO: Return 1 cluster
    #     subgraph = nx.complete_graph(8)
    #     if self.graph_type == "default":
    #         # subgraph = nx.generators.barabasi_albert_graph(self.num_of_nodes, self.initial_connections, seed=None)
    #         subgraph = self.buildConnectedClustersToSpec(self.get_default_settings())
    #
    #     # subgraph = self.actor_init_method(subgraph)
    #
    #     return subgraph

    def _build_graphs_to_detailed_description(self):
        graph = None
        return graph

    def _build_clusters_with_overlay(self):
        overlay = self.buildSingleGraph(self.overlay_type, self.num_of_clusters, self.overlay_initial_connections,
                                        self.overlay_branch_probability)
        overlay = self._apply_random_opinions(overlay)

        graph_list = []
        for idx in range(self.num_of_clusters):
            subgraph = self.buildSingleGraph(self.graph_type, self.num_of_nodes, self.initial_connections,
                                             self.branch_probability)
            subgraph = graph = self._apply_random_opinions(subgraph)
            graph_list.append(subgraph)

        return self.connect_clusters_by_overlay(overlay, graph_list)

    def create_graph_for_simulation(self):
        graph = self.setup_method()
        return graph


    # def _connected(self, clusters, connection=1):
    #     #TODO: all
    #     return clusters[0]

    def create(self):
        # TODO: all
        # node_distrebution = self.node_distribution_method(self.num_of_cluster)
        # clusters = []

        # for nodes in node_distrebution:
        #
        #     cluster = self._create_cluster(type=self.graph_type, num_of_nodes=nodes, initial_connections=self.initial_connections,
        #                                            probability=self.branch_probability)
        #
        #     clusters.append(cluster)
        #
        # g = self._connected(clusters)

        # g = self._create_cluster(type=self.graph_type, num_of_nodes=10, initial_connections=self.initial_connections,
        #                                            probability=self.branch_probability)
        g = self.create_graph_for_simulation()
        setVersion(g, 1.0)
        g = addConvenienceAttributes(calculateAttributes(g))
        return g

    @staticmethod
    def get_default_setup():
        graph = GraphFactory._buildConnectedClustersToSpec(GraphFactory.get_default_settings())
        return graph

    # @staticmethod
    # def get_default_settings():
    #     cluster0 = {'type': "complete", 'number_of_nodes': 25, 'initial_connections': 3, 'probability':0.4, 'pro_likelihood': 0.7, 'con_likelihood': 0.1, 'consense_indexes': [0, 1]}
    #     cluster1 = {'type': "complete", 'number_of_nodes': 15, 'initial_connections': 2, 'probability': 0.6, 'pro_likelihood': 0.5, 'con_likelihood': 0.3, 'consense_indexes': [1, 2]}
    #     cluster2 = {'type': "complete", 'number_of_nodes': 10, 'initial_connections': 2, 'probability': 0.6, 'pro_likelihood': 0.2, 'con_likelihood': 0.1, 'consense_indexes': [3]}
    #     cluster3 = {'type': "complete", 'number_of_nodes': 7, 'initial_connections': 2, 'probability': 0.6,
    #                 'pro_likelihood': 0.2, 'con_likelihood': 0.1, 'consense_indexes': [3]}
    #     cluster_list = [cluster0, cluster1, cluster2, cluster3]
    #     settings_dict = {'clusterList': cluster_list}
    #     return settings_dict

    @staticmethod
    def _get_merging_graphs_settings(cluster_a_size, cluster_b_size):
        cluster0 = {'type': "complete", 'number_of_nodes': cluster_a_size, 'initial_connections': 0, 'probability':0.0, 'pro_likelihood': 1.0, 'con_likelihood': 0.0, 'consense_indexes': [0, 1, 2, 3]}
        cluster1 = {'type': "complete", 'number_of_nodes': cluster_b_size, 'initial_connections': 0, 'probability': 0.0, 'pro_likelihood': 1.0, 'con_likelihood': 0.0, 'consense_indexes': [0, 1, 2, 3]}
        cluster_list = [cluster0, cluster1]
        settings_dict = {'clusterList': cluster_list}
        return settings_dict

    @staticmethod
    def _clone_opinions_with_div(source_oppinions):
        cloned_oppinions = copy.deepcopy(source_oppinions)
        # set divergent oppinion
        div_idx = random.randint(0, NUMBER_OF_KEY_OPINIONS)
        cloned_oppinions[div_idx] = random.randint(-1, +1)
        return cloned_oppinions

    @staticmethod
    def _apply_cloned_opinions_with_div(source_node, dest_node):
        original_oppinions = source_node[KEY_OPINIONS]
        dest_node[KEY_OPINIONS] = GraphFactory._clone_opinions_with_div(original_oppinions)
        return dest_node

    @staticmethod
    def _create_random_oppinions():
        opinions = []
        for i in range(NUMBER_OF_KEY_OPINIONS):
            opinions.append(random.randint(-1, 1))
        return opinions

    @staticmethod
    def _apply_random_opinions_to_node(node):
        """
        assigns random opinion to node
        """
        node[KEY_OPINIONS] = GraphFactory._create_random_oppinions()
        return node

    @staticmethod
    def _apply_random_opinions(graph):
        """
        assigns random opinions to all nodes
        """
        if graph is None:
            return None
        for nodeId in graph.node:
            GraphFactory._apply_random_opinions_to_node(graph.node[nodeId])
        return graph

    @staticmethod
    def _apply_specific_common_opinion_to_node(node, pro_likelihood, con_likelihood, opinion_index):
        """
        assigns opinions to node, adhering to given likelihoods
        """
        rand = random.uniform(0, 1)
        if rand <= pro_likelihood:
            node[KEY_OPINIONS][opinion_index] = 1
        elif rand >= 1 - con_likelihood:
            node[KEY_OPINIONS][opinion_index] = -1
        else:
            node[KEY_OPINIONS][opinion_index] = 0
        return node

    @staticmethod
    def _apply_specific_common_opinion(graph, pro_likelihood, con_likelihood, opinion_index):
        """
        assigns opinions to graphs nodes, adhering to given likelihoods
        """
        opinion_index = opinion_index % NUMBER_OF_KEY_OPINIONS
        if graph is None:
            return None
        for nodeId in graph.node:
            node = graph.node[nodeId]
            GraphFactory._apply_specific_common_opinion_to_node(node, pro_likelihood, con_likelihood, opinion_index)
        graph = calculateAttributes(graph)
        return graph

    @staticmethod
    def _apply_alternating_opinions(graph, index_list):
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
    def _apply_opinions(graph, pro_likelihood, con_likelihood, opinion_indexes):
        """
        assigns opinions to graphs nodes, adhering to given likelihoods
        """
        if graph is None:
            return None
        graph = GraphFactory._apply_random_opinions(graph)

        for idx in opinion_indexes:
            graph = GraphFactory._apply_specific_common_opinion(graph, pro_likelihood, con_likelihood, idx)


        graph = calculateAttributes(graph)

        return graph

    @staticmethod
    def connect_clusters(graphs):
        """
        inserts edges between given graphs to create connected graph
        """
        return GraphFactory.connect_clusters_n_times(graphs, 1)

    @staticmethod
    def connect_clusters_n_times(graphs, number_of_times):
        """
        inserts edges between given graphs to create connected graph
        """
        cpy = copy.deepcopy(graphs)
        if graphs is None or len(graphs) == 0:
            return None

        used_edges = []
        current_edge = [-1, -1]
        used_edges.append(current_edge)
        result_graph = cpy.pop()

        while len(cpy) > 0:
            rand = random.randint(0, len(cpy)-1)    #select subgraph to add
            subgraph = cpy.pop(rand)
            offset_to_new_nodes = nx.number_of_nodes(result_graph)
            subgraph_number_of_nodes = nx.number_of_nodes(subgraph)
            result_graph = nx.disjoint_union(result_graph, subgraph)
            #connect by random edge connected to graph

            node_idx_1 = 0
            node_idx_2 = 0
            for i in range(number_of_times):

                while current_edge in used_edges:
                    node_idx_1 = random.randint(0, offset_to_new_nodes - 1)
                    node_idx_2 = offset_to_new_nodes + random.randint(0, subgraph_number_of_nodes - 1)
                    current_edge = [node_idx_1, node_idx_2]
                #
                result_graph.add_edge(node_idx_1, node_idx_2)
                used_edges.append(current_edge)
        print(used_edges)
        return result_graph

    @staticmethod
    def connect_clusters_by_overlay(overlay_graph, subgraphs):
        """
        inserts subgraphs as edges between given graphs into overlay
        """

        if subgraphs is None or len(subgraphs) == 0:
            return None

        cpy = copy.deepcopy(subgraphs)
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
    def connect_clusters_by_overlay(overlay_graph, subgraphs):
        """
        inserts subgraphs as edges between given graphs into overlay
        """

        if subgraphs is None or len(subgraphs) == 0:
            return None

        cpy = copy.deepcopy(subgraphs)
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

    def _build_dissociating_graph(self):
        graph = self.buildSingleGraph(self.graph_type, self.num_of_nodes, self.initial_connections, self.branch_probability)
        graph = self._apply_random_opinions(graph)
        graph = self._apply_alternating_opinions(graph, self.consense_indexes)
        return graph

    def _buildConnectedClustersToSpec(self):
        """
        creates creates initialised connected clusters
        """
        # self._get_merging_graphs_settings(self.num_of_nodes, self.num_of_nodes), self.number_of_interconnections
        settings_dict = self._get_merging_graphs_settings(self.num_of_nodes, self.num_of_nodes)
        interconnections = self.number_of_interconnections
        subgraphs = []

        clusterList = settings_dict['clusterList']

        for cluster_id in range(len(clusterList)):
            type = clusterList[cluster_id]['type']
            number_of_nodes = clusterList[cluster_id]['number_of_nodes']
            initial_connections = clusterList[cluster_id]['initial_connections']
            probability = clusterList[cluster_id]['probability']
            subgraph = GraphFactory.buildSingleGraph(type, number_of_nodes, initial_connections, probability)
            subgraph = GraphFactory._apply_opinions(subgraph, clusterList[cluster_id]['pro_likelihood'], clusterList[cluster_id]['con_likelihood'], clusterList[cluster_id]['consense_indexes'])
            subgraphs.append(subgraph)
        resultGraph = GraphFactory.connect_clusters_n_times(subgraphs, interconnections)
        # resultGraph = GraphFactory.connect_clusters(subgraphs)
        return resultGraph

    def _buildConnectedClustersToSpecList(self):
        """
        creates creates initialised connected clusters
        """
        subgraph_list = self.subgraph_list
        num_of_interconnections = self.number_of_interconnections
        subgraphs_with_attributes = []
        for idx in range(len(subgraph_list)):
            type = subgraph_list[idx]['type']
            number_of_nodes = subgraph_list[idx]['number_of_nodes']
            initial_connections = subgraph_list[idx]['initial_connections']
            probability = subgraph_list[idx]['probability']
            subgraph = GraphFactory.buildSingleGraph(type, number_of_nodes, initial_connections, probability)
            subgraph = GraphFactory._apply_opinions(subgraph, subgraph_list[idx]['pro_likelihood'], subgraph_list[idx]['con_likelihood'], subgraph_list[idx]['consense_indexes'])
            subgraphs_with_attributes.append(subgraph)
        resultGraph = GraphFactory.connect_clusters_n_times(subgraphs_with_attributes, num_of_interconnections)
        return resultGraph

    def neu_buildConnectedClustersToSpecList(self):
        """
        creates creates initialised connected clusters
        """
        subgraph_list = self.subgraph_list
        num_of_interconnections = self.number_of_interconnections
        subgraphs_with_attributes = []
        for idx in range(len(subgraph_list)):
            subgraph = GraphFactory.build_single_graph_with_oppinions(subgraph_list[idx])
            subgraphs_with_attributes.append(subgraph)
        resultGraph = GraphFactory.connect_clusters_n_times(subgraphs_with_attributes, num_of_interconnections)
        return resultGraph

    def _buildClustersWithCoreness(self):
        """
        Creates clusters with opinions deviating with descending coreness
        :return: the resulting graph
        """
        subgraph_List = self.subgraph_list
        num_of_interconnections = self.number_of_interconnections
        subgraphs_with_attributes = []
        for idx in range(len(subgraph_List)):
            type = subgraph_List[idx]['type']
            number_of_nodes = subgraph_List[idx]['number_of_nodes']
            initial_connections = subgraph_List[idx]['initial_connections']
            probability = subgraph_List[idx]['probability']
            subgraph = GraphFactory.buildSingleGraph(type, number_of_nodes, initial_connections, probability)
            subgraph = GraphFactory._applyOpinionsUsingCoreness(subgraph)
            subgraphs_with_attributes.append(subgraph)
        resultGraph = GraphFactory.connect_clusters_n_times(subgraphs_with_attributes, num_of_interconnections)

        return resultGraph

    @staticmethod
    def _apply_fixed_oppinions(graph, graph_dict):
        for i in range(nx.number_of_nodes(graph)):
            graph.nodes()[i][KEY_OPINIONS] = graph_dict[OPPINION_DISTRIBUTION_FIXED]

    @staticmethod
    def _applyOpinionsUsingCoreness(graph):
        core_group_map = GraphFactory._core_groups(graph)
        descending_order_keylist = sorted(core_group_map, reverse=True)

        prev_oppinions = GraphFactory._create_random_oppinions()
        for coreness_key in descending_order_keylist:
            div_oppinions = GraphFactory._clone_opinions_with_div(prev_oppinions)
            for node_idx in core_group_map[coreness_key]:
                for idx in range(NUMBER_OF_KEY_OPINIONS):
                    graph.node[node_idx][idx] = div_oppinions[idx]

                # subgraph.node[node_idx] = div_oppinions
            prev_oppinions = div_oppinions

        return graph

    @staticmethod
    def buildSingleGraph(type, number_of_nodes, initial_connections, probability):
        """
        creates creates initialised connected clusters
        """
        if type == "Barabasi-Albert":
            graph = nx.generators.barabasi_albert_graph(number_of_nodes, initial_connections, seed=None)
        elif type == "Watts-Strogatz":
            graph = nx.generators.connected_watts_strogatz_graph(number_of_nodes, initial_connections, probability, DEFAULT_NUMBER_OF_ATTEMPTS, seed=None)
        elif type == "Powerlaw-Cluster":
            graph = nx.powerlaw_cluster_graph(number_of_nodes, initial_connections, probability, seed=None)
        else:
            graph = nx.generators.complete_graph(number_of_nodes)
        return graph

    # test
    @staticmethod
    def _set_oppinins(graph, graph_dict):
        distr_type = graph_dict[GRAPH_OPPINION_DISTRIBUTION_TYPE]
        if distr_type == OPPINION_DISTRIBUTION_SPECIFIC:
            graph = GraphFactory._apply_opinions(graph, graph_dict[GRAPH_PRO_LIKELIHOOD], graph_dict[GRAPH_CON_LIKELIHOOD], graph_dict[GRAPH_CONSENSE_INDEXES])
        elif distr_type == OPPINION_DISTRIBUTION_ALTERNATING:
            graph = GraphFactory._apply_alternating_opinions(graph, graph_dict[GRAPH_CONSENSE_INDEXES])
        elif distr_type == GRAPH_OPPINION_FIXED_LIST:
            graph = GraphFactory._apply_fixed_oppinions(graph, graph_dict[GRAPH_OPPINION_FIXED_LIST])
        else:
            graph = GraphFactory._apply_random_opinions(graph)
        return graph


    @staticmethod
    def build_single_graph_with_oppinions(graph_dict):
        """
        creates creates initialised connected clusters
        """
        type = graph_dict[GRAPH_TYPE]
        number_of_nodes = graph_dict[GRAPH_NUMBER_OF_NODES]
        initial_connections = graph_dict[GRAPH_NUMBER_OF_INITIAL_CONNECTIONS]
        probability = graph_dict[GRAPH_BRANCH_PROBABILITY]
        if type == GRAPH_TYPE_BARABASI:
            graph = nx.generators.barabasi_albert_graph(number_of_nodes, initial_connections, seed=None)
        elif type == GRAPH_TYPE_WATTS_STROGATZ:
            graph = nx.generators.connected_watts_strogatz_graph(number_of_nodes, initial_connections, probability, DEFAULT_NUMBER_OF_ATTEMPTS, seed=None)
        elif type == GRAPH_TYPE_POWERLAW:
            graph = nx.powerlaw_cluster_graph(number_of_nodes, initial_connections, probability, seed=None)
        else:
            graph = nx.generators.complete_graph(number_of_nodes)
        graph = GraphFactory._set_oppinins(graph, graph_dict)

        # graph = GraphFactory._set_oppinins(graph, graph_dict)

        return graph

    def buildEqualConnectedClustersToSpec(self):
        """
        creates creates initialised connected clusters
        """
        type = self.graph_type
        num_of_clusters = self.num_of_clusters
        number_of_nodes = self.num_of_nodes
        initial_connections = self.initial_connections
        probability = self.branch_probability
        pro_likelihood = self.pro_likelihood
        con_likelihood = self.con_likelihood
        consense_indexes = self.consense_indexes
        number_of_interconnections = self.number_of_interconnections

        subgraphs = []

        for cluster_id in range(num_of_clusters):
            subgraph = GraphFactory.buildSingleGraph(type, number_of_nodes, initial_connections, probability)
            subgraph = GraphFactory._apply_opinions(subgraph, pro_likelihood, con_likelihood, consense_indexes)
            subgraphs.append(subgraph)
        resultGraph = GraphFactory.connect_clusters_n_times(subgraphs, number_of_interconnections)
        return resultGraph

    def _core_groups(cluster):
        """
        creates dictionary mapping lists of all node IDs to their coreness

        :param cluster: the evaluated graph
        :return: node ID dictionary
        """
        core_dict = nx.core_number(cluster)
        # print(core_dict)
        result_dict = {}.fromkeys(set(core_dict.values()), [])

        for key in core_dict:
            result_dict[core_dict[key]].append(key)

        return result_dict