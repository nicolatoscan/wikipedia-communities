import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from networkx.algorithms.community import k_clique_communities


def generate_network(n):
    graph_dct = {node: [] for node in range(n)}
    nodes = list(range(n))

    # generate edges
    for n, edge_list in graph_dct.items():
        edge_c = random.randint(min(nodes), int(max(nodes) / 5))
        el = random.sample(nodes, edge_c)
        graph_dct[n] = el

    G = nx.MultiGraph(graph_dct)
    return G


def build_block_of_cummunities(G, com_dict, com_number):
    V = [node for node in G.nodes()]
    com = [[V[i] for i in range(G.number_of_nodes()) if com_dict[i] == j] for j in range(com_number)]
    return com


def number_of_community(com_dict):
    unique_coms = np.unique(list(com_dict.values()))
    return max(unique_coms) + 1


def build_visualization_graph(com, com_dict, G):
    G_graph = nx.Graph()
    for each in com:
        G_graph.update(nx.subgraph(G, each))
    color = [com_dict[node] for node in G_graph.nodes()]
    return [color, G_graph]


def community_visualization(G_graph, G, color):
    pos = nx.spring_layout(G_graph, seed=4, k=0.33)
    nx.draw(G, pos, with_labels=False, node_size=1, width=0.1, alpha=0.2)
    nx.draw(G_graph, pos, with_labels=True, node_color=color, node_size=70, width=0.5, font_size=5,
            font_color='#000000')
    plt.show()


def find_community(graph, k):
    return list(k_clique_communities(graph, k))


def build_dict1(G, coms):
    V = [node for node in G.nodes()]
    com_dict = {node: com for node, com in zip(V, coms)}
    return com_dict


def bulid_dict2(com_dict):
    node_set = []
    com_set = []
    for i in range(len(com_dict)):
        set = list(com_dict[i])
        for j in range(len(set)):
            node_set.append(set[j])
            com_set.append(i)
    com_dict1 = {node_set[i]: com_set[i] for i in range(len(node_set))}
    return com_dict1

