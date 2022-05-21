import numpy as np

import Functions
import networkx as nx
from community import community_louvain
from networkx import community
import matplotlib.pyplot as plt
import copy
import Girvan_Newman as GN
from networkx.algorithms.community import k_clique_communities

n = 300 # number of nodes
G = Functions.generate_network(n)  # generate graph
print(nx.info(G))  # show graph information (nodes and edges)

# visualize graph
pos = nx.spring_layout(G)
nx.draw(G, pos, node_size=70, width=0.5, font_size=5, font_color='#000000')
plt.show()

# Louvain method detect communities
louvain_com_dict = community_louvain.best_partition(G)  # Louvain communities dictionary
unique_louvain_com = Functions.number_of_community(louvain_com_dict)  # Number of communities have been detected
Louvain_coms = Functions.build_block_of_cummunities(G, louvain_com_dict, unique_louvain_com)  # Community blocks
[Louvain_color, Louvain_Graph] = Functions.build_visualization_graph(Louvain_coms, louvain_com_dict, G)
Functions.community_visualization(Louvain_Graph, G, Louvain_color)

# K-clique method detect communities
for k in range(5,10):
    print("K-Clique: %d" % k)
    k_clique_coms = Functions.find_community(G, k)
    print("Count of Community being found: %d" % len(k_clique_coms))
    print(k_clique_coms)

# Girvan_Newman method detect communities
'''G_copy = copy.deepcopy(G)
gn_com, gm_modularity = GN.partition(G_copy)
gn_com_dict = Functions.build_dict1(G, gn_com)
unique_gn_com = Functions.number_of_community(gn_com_dict)
gn_coms = Functions.build_block_of_cummunities(G, gn_com_dict, unique_gn_com)
[gn_color, gn_graph] = Functions.build_visualization_graph(gn_coms, gn_com_dict, G)
Functions.community_visualization(gn_graph, G, gn_color)'''


# Greedy modularity method detect communities
GM_com = community.greedy_modularity_communities(G)
GM_com_dict = Functions.build_dict1(G, GM_com)
GM_com_dict = Functions.bulid_dict2(GM_com_dict)
unique_GM_com = Functions.number_of_community(GM_com_dict)
GM_coms = Functions.build_block_of_cummunities(G, GM_com_dict, unique_GM_com)
GM_color, GM_Graph = Functions.build_visualization_graph(GM_coms, GM_com_dict, G)
Functions.community_visualization(GM_Graph, G, GM_color)

# 

