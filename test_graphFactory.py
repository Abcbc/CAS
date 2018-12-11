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
        settings = cnf.load_config()[0]  # get list of settings
        factory = gf.GraphFactory(settings)  # get specialized factory
        g = factory._build_dissociating_graph()
        nx.draw(g)
        plt.show()
