import networkx as nx
import random
import Graph
import community
import numpy as np


def get_graph(graph_settings, opinion_settings, get_addl_info=False):
    g = nx.Graph()
    if graph_settings['graph_type'] == 'Erdos-Renyi':
        g = nx.erdos_renyi_graph(graph_settings['graph_num_of_nodes'],graph_settings['graph_erdos_renyi_edge_prob'])
    elif graph_settings['graph_type'] == 'Barabasi-Albert':
        g = nx.barabasi_albert_graph(graph_settings['graph_num_of_nodes'],graph_settings['graph_barabasi_albert_n-conn'])
    elif graph_settings['graph_type'] == '2BA':
        graph_part_size = graph_settings['graph_part_num_of_nodes']
        g1 = nx.barabasi_albert_graph(graph_part_size,graph_settings['graph_barabasi_albert_n-conn'])
        g2 = nx.barabasi_albert_graph(graph_part_size,graph_settings['graph_barabasi_albert_n-conn'])
        g = nx.Graph()
        g.add_edges_from([(e[0],e[1]) for e in g1.edges])
        g.add_edges_from([(e[0]+graph_part_size,graph_part_size+e[1]) for e in g2.edges])
        g.add_edges_from([(random.choice(range(graph_settings['graph_part_num_of_nodes'])),random.choice(range(graph_part_size,graph_part_size+graph_settings['graph_part_num_of_nodes']))) for _ in range(graph_settings['graph_inter_cluster_connections'])])
    elif graph_settings['graph_type'] == 'karate-club':
        g = nx.karate_club_graph()

    if opinion_settings['opinions_distri'] == 'different':
        for nid in g.nodes:
            g.nodes[nid]['opinions'] = [1 if random.random() < opinion_settings['opinions_pos_ratio'] else -1 for _ in range(opinion_settings['opinions_number_of_topics'])]
    elif opinion_settings['opinions_distri'] == 'same+different':
        for nid in g.nodes:
            if random.random() < opinion_settings['opinions_pos_ratio']:
                g.nodes[nid]['opinions'] = [1 for _ in range(opinion_settings['opinions_number_of_same_topics'])]+[1 for _ in range(opinion_settings['opinions_number_of_different_topics'])]
            else:
                g.nodes[nid]['opinions'] = [1 for _ in range(opinion_settings['opinions_number_of_same_topics'])]+[-1 for _ in range(opinion_settings['opinions_number_of_different_topics'])]
    elif opinion_settings['opinions_distri'] == 'neutral+different':
        for nid in g.nodes:
            if random.random() < opinion_settings['opinions_pos_ratio']:
                g.nodes[nid]['opinions'] = [0 for _ in range(opinion_settings['opinions_number_of_neutral_topics'])]+[1 for _ in range(opinion_settings['opinions_number_of_different_topics'])]
            else:
                g.nodes[nid]['opinions'] = [0 for _ in range(opinion_settings['opinions_number_of_neutral_topics'])]+[-1 for _ in range(opinion_settings['opinions_number_of_different_topics'])]
    elif opinion_settings['opinions_distri'] == 'random':
        for nid in g.nodes:
            ops = [-1,0,1]
            g.nodes[nid][Graph.KEY_OPINIONS] = random.choices(ops,k=opinion_settings['opinions_number_of_topics'])
    elif opinion_settings['opinions_distri'] == 'model':
        bp = community.best_partition(g)
        comms = [[nid for nid in community.best_partition(g) if bp[nid]==i] for i in range(20)]
        comms = [comm for comm in comms if len(comm)>0]
        if community.modularity(bp,g) < 0.2:
            comms = [list(g.nodes)]

        centre_ids = []
        for comm in comms:
            if opinion_settings['opinions_center_choicemode'] == 'degree':
                sg = nx.subgraph(g,comm)
                degs = nx.degree(sg)
                weights = np.array([1/degs[nid] for nid in sg.nodes])
                centre_ids.extend(np.random.choice([nid for nid in sg.nodes],size=opinion_settings['opinions_number_of_centres'],replace=False,p=weights/np.sum(weights)))
            elif opinion_settings['opinions_center_choicemode'] == 'betweenness':
                sg = nx.subgraph(g,comm)
                betw = nx.betweenness_centrality(sg)
                while np.sum(np.array([betw[nid] for nid in sg.nodes]) > 0) < opinion_settings['opinions_number_of_centres']:
                    betw[random.choice(list(betw.keys()))] += 0.1
                weights=np.array([betw[nid] for nid in sg.nodes])
                p = weights/np.sum(weights) if np.sum(weights) != 0 else [1/len(weights) for i in range(len(weights))]
                centre_ids.extend(np.random.choice([nid for nid in sg.nodes],size=opinion_settings['opinions_number_of_centres'],replace=False,p=p))
            elif opinion_settings['opinions_center_choicemode'] == 'periph':
                sg = nx.subgraph(g,comm)
                ecc = nx.eccentricity(sg)
                maxInd = max(ecc,key=lambda d: ecc[d])
                maxEcc = ecc[maxInd]
                shell = [nid for nid in sg.nodes if ecc[nid] == maxEcc]
                i=1
                while len(shell) < opinion_settings['opinions_number_of_centres']:
                    shell.extend([nid for nid in sg.nodes if ecc[nid] == maxEcc-i])
                centre_ids.extend(np.random.choice([nid for nid in sg.nodes],size=opinion_settings['opinions_number_of_centres'],replace=False))
        # print(centre_ids)

        for c_id in centre_ids:
            g.nodes[c_id][Graph.KEY_OPINIONS] = random.choices([0,1,-1],k=opinion_settings['opinions_number_of_topics'])
        if opinion_settings['opinions_center_tendencies'] != 'random':
            if len(opinion_settings['opinions_center_tendencies']) < len(centre_ids):
                print('len(tendencies) {} < len(centre ids) {} => repeating sequence (config:{},{})'.format(len(opinion_settings['opinions_center_tendencies']),len(centre_ids),graph_settings,opinion_settings))
                while len(opinion_settings['opinions_center_tendencies']) < len(centre_ids):
                    opinion_settings['opinions_center_tendencies'] += opinion_settings['opinions_center_tendencies']

            for tendency, c_id in zip(opinion_settings['opinions_center_tendencies'], centre_ids):
                weights = [1,1,1]
                weights[{'neg':0,'neu':1,'pos':2}[tendency]] = opinion_settings['tendency_strength'] #8
                g.nodes[c_id][Graph.KEY_OPINIONS] = random.choices([-1,0,1],k=opinion_settings['opinions_number_of_topics'],weights=weights)
        ops = [[g.nodes[c_id][Graph.KEY_OPINIONS][t_id] for c_id in centre_ids] + [-1,0,1] for t_id in range(opinion_settings['opinions_number_of_topics'])]

        diameter = nx.diameter(g)
        for nid in g:
            if nid in centre_ids:
                continue
            func = lambda dist: 1/dist
            if opinion_settings['func'] == 'log':
                func = lambda dist:pow(10,-dist)
            opinions = []
            for t_id in range(opinion_settings['opinions_number_of_topics']):
                dists = [nx.shortest_path_length(g,nid,c_id) for c_id in centre_ids]
                weights = [func(dist) for dist in dists]
                weights += [func(2*diameter)]*3 if opinion_settings['func'] != 'log' else [func(diameter)]*3
                opinions.append(random.choices(ops[t_id], weights,k=1)[0])
            g.nodes[nid][Graph.KEY_OPINIONS] = opinions

    g = Graph.calculateAttributes(g)
    g = Graph.addConvenienceAttributes(g)
    Graph.setVersion(g,0)
    return g

"""
graph_type: Erdos-Renyi, arabasi-Albert
graph_num_of_nodes: int
graph_erdos_renyi_edge_prob: 0...1
graph_erdos_renyi_edge_prob: 0...1
graph_barabasi_albert_n-conn: 1...graph_num_of_nodes

opinions_distri: different, same+different, neutral+different
opinions_number_of_topics: int
opinions_number_of_same_topics: int
opinions_number_of_different_topics: int
opinions_number_of_neutral_topics: int
opinions_pos_ratio: 0...1
"""
