from unittest import TestCase
import utils.ConfigLoader as cnf
import GraphFactory as gf
import networkx as nx
import matplotlib.pyplot as plt

class TestGraphFactory(TestCase):

    def test_building_multiple_setups(self):
        settings_list = cnf.load_config()                       #get list of settings; use first entry

        # settings_merging = settings_list[0]
        # factory_merging = gf.GraphFactory(settings_merging)     #get specialized factory
        # gm = factory_merging.create()                           #get graph
        # nx.draw(gm)
        # plt.show()
        #
        # settings_dissociating = settings_list[1]
        # factory_dissociating = gf.GraphFactory(settings_dissociating)
        # gd = factory_dissociating.create()
        # nx.draw(gd)
        # plt.show()
        #
        # settings_overlay = settings_list[2]
        # factory_overlay = gf.GraphFactory(settings_overlay)
        # go = factory_overlay.create()
        # nx.draw(go)
        # plt.show()
        #
        # settings_diverse_clusters = settings_list[3]
        # factory_diverse_clusters = gf.GraphFactory(settings_diverse_clusters)
        # gdiv = factory_diverse_clusters.create()
        # nx.draw(gdiv)
        # plt.show()
        #
        # settings_default = settings_list[4]
        # factory_default = gf.GraphFactory(settings_default)
        # gdef = factory_default.create()
        # nx.draw(gdef)
        # plt.show()

        settings_default = settings_list[5]
        factory_default = gf.GraphFactory(settings_default)
        gcore = factory_default.create()
        nx.draw(gcore)
        plt.show()

        settings_neu = settings_list[6]
        factory_neu = gf.GraphFactory(settings_neu)
        gneu = factory_neu.create()
        nx.draw(gneu)
        plt.show()

        # self.assertTrue(gm != None)
        # self.assertTrue(gd != None)
        # self.assertTrue(go != None)
        # self.assertTrue(gdef != None)
        # self.assertTrue(gdiv != None)
        # self.assertTrue(gcore != None)

    def test_building_diverse_setup(self):
        settings_list = cnf.load_config()
        settings_diverse_clusters = settings_list[3]
        factory_diverse_clusters = gf.GraphFactory(settings_diverse_clusters)
        gdiv = factory_diverse_clusters.create()
        nx.draw(gdiv)
        plt.show()
        self.assertTrue(gdiv != None)

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

    def test_get_default_setup(self):
        # settingsDict = GraphFactory.get_default_settings()
        n = gf.NUMBER_OF_KEY_OPINIONS
        print(gf.NUMBER_OF_KEY_OPINIONS)

        assert(n != 0)
