def testGraphLogWriteRead():
    g = buildGraph()

    j = toJsonStr(g)

    g2 = fromJsonStr(j)

    for nodeId in g.nodes:
        node = g.nodes[nodeId]
        node2 = g2.nodes[nodeId]
        if node[KEY_NODE_ID] != node2[KEY_NODE_ID] or node[KEY_OPINIONS] != node2[KEY_OPINIONS] or node[KEY_SPECTRUM] != node2[KEY_SPECTRUM]:
            return False
    for edgeId in g.edges:
        edge = g.edges[edgeId]
        edge2 = g2.edges[edgeId]
        if edge[KEY_EDGE_ID] != edge2[KEY_EDGE_ID] or edge[KEY_ORIENTATION] != edge2[KEY_ORIENTATION]:
            return False

    return True
