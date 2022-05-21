import networkx as nx
import community as cm
import copy


def all_results(G):
    results = []
    m = G.number_of_edges()
    for i in range(m):
        betweenness_dict = nx.edge_betweenness_centrality(G)
        edge_max_betweenness = max(betweenness_dict.items(), key=lambda x: x[1])[0]
        G.remove_edge(edge_max_betweenness[0], edge_max_betweenness[1])
        community = [list(subgraph) for subgraph in nx.connected_components(G)]
        community_dict = {node: 0 for node in G.nodes()}
        for i in range(len(community)):
            each = community[i]
            for node in each:
                community_dict[node] = i
        results.append(community_dict)
    return results


def partition(G):
    G_copy = copy.deepcopy(G)
    results = all_results(G)
    modularities = [cm.modularity(results[i], G_copy) for i in range(len(results))]
    max_modularity = max(modularities)
    max_index = modularities.index(max_modularity)
    max_result = results[max_index]
    return list(max_result.values()), max_modularity
