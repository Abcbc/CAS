if __name__ == '__main__':
    import Analyser
    import numpy as np
    import matplotlib.pyplot as plt
    import MyGraphFactory
    ratios = []
    means = []
    stds = []
    for ratio100 in range(0,101):
        ratio = ratio100 / 100
        g_settings = {'graph_type': "Erdos-Renyi",
                'graph_erdos_renyi_edge_prob': 0.3,
                'graph_num_of_nodes': 50}
        o_settings = {
                'opinions_distri': 'different',
                'opinions_number_of_topics': 50,
                'opinions_pos_ratio': ratio}
        ms = []
        for i in range(100):
            g = MyGraphFactory.get_graph(g_settings, o_settings)
            m = Analyser.MetricOpinionConsensus()
            ms.append(m.calculate(g))
        ratios.append(ratio)
        means.append(np.mean(ms))
        stds.append(np.std(ms))
    plt.figure()
    plt.plot(ratios,means)
    plt.xlabel('ratio of opinion 1')
    plt.ylabel('OpinionConsensus')
    plt.title('ER-Graph, n=50,p=0.3')
    plt.savefig('ConsensusER.png')
    plt.figure()
    plt.plot(ratios,stds)
    plt.xlabel('ratio of opinion 1')
    plt.ylabel('OpinionConsensus')
    plt.title('Std of ER-Graph, n=50,p=0.3')
    plt.savefig('ConsensusER_std.png')


    ratios = []
    means = []
    stds = []
    for ratio100 in range(0,101):
        ratio = ratio100 / 100
        g_settings = {'graph_type': "Barabasi-Albert",
                'graph_barabasi_albert_n-conn': 5,
                'graph_num_of_nodes': 50}
        o_settings = {
                'opinions_distri': 'different',
                'opinions_number_of_topics': 50,
                'opinions_pos_ratio': ratio}
        ms = []
        for i in range(100):
            g = MyGraphFactory.get_graph(g_settings, o_settings)
            m = Analyser.MetricOpinionConsensus()
            ms.append(m.calculate(g))
        ratios.append(ratio)
        means.append(np.mean(ms))
        stds.append(np.std(ms))
    plt.figure()
    plt.plot(ratios,means)
    plt.xlabel('ratio of opinion 1')
    plt.ylabel('OpinionConsensus')
    plt.title('BA-Graph, n=50,m=5')
    plt.savefig('ConsensusBA.png')
    plt.figure()
    plt.plot(ratios,stds)
    plt.xlabel('ratio of opinion 1')
    plt.ylabel('OpinionConsensus')
    plt.title('Std of BA-Graph, n=50,m=5')
    plt.savefig('ConsensusBA_std.png')

    plt.show()
