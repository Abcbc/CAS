from unittest import TestCase
import utils.ConfigLoader as cnf
import GraphFactory as gf
import networkx as nx
import matplotlib.pyplot as plt

class TestGraphFactory(TestCase):
    def test_get_default_setup(self):
        # settingsDict = GraphFactory.get_default_settings()
        n = gf.NUMBER_OF_KEY_OPINIONS
        print(gf.NUMBER_OF_KEY_OPINIONS)

        assert(n != 0)

    def test_graph_building(self):
        settings = cnf.load_config()[0]         #get list of settings; use first entry
        factory = gf.GraphFactory(settings)     #get specialized factory
        g = factory.create()                    #get graph

        nx.draw(g)
        plt.show()

        assert(g != None)

    def test_core_groups(self):
        settings = cnf.load_config()[0]  # get list of settings
        factory = gf.GraphFactory(settings)  # get specialized factory
        g = factory.create()
        print(factory._core_groups(g))

    def test_merging_graphs_setup(self):
        settings = cnf.load_config()[0]  # get list of settings
        factory = gf.GraphFactory(settings)  # get specialized factory
        g = factory.buildConnectedClustersToSpec(factory._get_merging_graphs_settings(10, 15), 7)
        nx.draw(g)
        plt.show()

    def test_dissociating_graphs_setup(self):
        settings = cnf.load_config()[0]  # get list of settings
        factory = gf.GraphFactory(settings)  # get specialized factory
        g = factory._build_dissociating_graph()
        nx.draw(g)
        plt.show()

    def test_overlay_graphs_setup(self):
        # ot = self.overlay_type

        settings = cnf.load_config()[0]  # get list of settings
        factory = gf.GraphFactory(settings)  # get specialized factory

        overlay_graph = factory.buildSingleGraph(factory.overlay_type, factory.num_of_clusters,
                                                 factory.overlay_initial_connections, factory.overlay_branch_probability)
        graph_list = []
        for idx in range(factory.num_of_clusters):
            graph_list.append(factory.buildSingleGraph(factory.graph_type, factory.num_of_nodes, factory.initial_connections, factory.branch_probability))
        g = factory.connect_clusters_by_overlay(overlay_graph, graph_list)
        nx.draw(g)
        plt.show()
