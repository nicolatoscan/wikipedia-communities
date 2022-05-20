# %% imports
from typing import Counter
import networkx as nx
import networkx.algorithms.community as nx_comm
import networkx.algorithms.smallworld as nx_sw
import networkx.algorithms.components as nx_comp
import networkx.algorithms.cluster as nx_cluster
from tqdm import tqdm
import matplotlib.pyplot as plt

# %% graph
g = nx.Graph()
# g = nx.DiGraph()
# g = nx.MultiDiGraph()
with open('dataset/wikitalk.txt', 'r') as f:
    print('Importing data...')
    data =  [ list(map(int, line.strip().split(' '))) for line in list(f) ]

    print('Adding nodes ...')
    nodes = set([item for sublist in data for item in sublist[0:2]])
    g.add_nodes_from(nodes)

    print('Adding edges...')
    edges =  [ [info[0], info[1], { 'time': info[2] } ] for info in data ]
    g.add_edges_from(edges)

    print('Done!')
    del data
    del nodes
    del edges


# %% usernames
users = {}
idToUsername = {}
with open('dataset/usernames.txt', 'r') as f:
    for line in tqdm(f):
        id, username = line.strip('\n').split(' ')
        users[username] = int(id)
        idToUsername[int(id)] = username


# %% add props
genderMap = { 'female': 1, 'male': 0, 'unknown': -1 }
with open('dataset/userinfo.tsv', 'r') as f:
    for line in tqdm(f):
        data = line.strip('\n').split('\t')
        if len(data) == 6:
            id, name, gender, editcount, firstedit, roles = line.strip('\n').split('\t')
            if name in users:
                id = users[name]
                g.nodes[id]['id'] = id
                g.nodes[id]['name'] = name
                g.nodes[id]['gender'] = genderMap[gender]
                g.nodes[id]['roles'] = roles.split(',')

for id in tqdm(g.nodes):
    if 'id' not in g.nodes[id]:
        g.nodes[id]['id'] = -1
        g.nodes[id]['name'] = idToUsername[id]
        g.nodes[id]['gender'] = -1
        g.nodes[id]['roles'] = [ '*' ]


# %% basic stats
nrFema = sum([ 1 for n in g.nodes(data=True) if n[1]['gender'] ==  1 ])
nrMale = sum([ 1 for n in g.nodes(data=True) if n[1]['gender'] ==  0 ])
nrUnkn = sum([ 1 for n in g.nodes(data=True) if n[1]['gender'] == -1 ])

# %%
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Users gender distribution')
ax1.pie([ nrUnkn, nrMale + nrFema ],    labels=['Unknown', 'Known'],    colors=['tab:gray', 'tab:green'], autopct='%1.1f%%')
ax2.pie([ nrFema, nrMale ],             labels=['Female', 'Male'],      colors=['tab:orange', 'tab:blue'], autopct='%1.1f%%')
plt.show()

# %%
# communities = nx_comm.louvain_communities(g)
# parts = nx_comm.louvain_partitions(g)
# %% coverage
female = [ n[0] for n in g.nodes(data=True) if n[1]['gender'] ==  1 ]
male = [ n[0] for n in g.nodes(data=True) if n[1]['gender'] ==  0 ]


# %%
nx_comm.coverage(g, [ female, male, set(g.nodes) - set(female) - set(male) ])
# %%
nx_comm.coverage(g, [ female, set(g.nodes) - set(female) ])
# %%
nx_comm.coverage(g, [ male, set(g.nodes) - set(male) ])
# %%
nx_sw.sigma(g)
# %%
nx_sw.omega(g)

# %%
nx_comm.greedy_modularity_communities(g)
# %%
nx_comp.is_weakly_connected(g)
# %%
weak = list(nx_comp.weakly_connected_components(g))
strong = list(nx_comp.strongly_connected_components(g))
# %%
roles = Counter()
for n in g.nodes(data=True):
    roles.update(n[1]['roles'])
# %%
sysop = [ n[0] for n in g.nodes(data=True) if 'sysop' in n[1]['roles'] ]
bots = [ n[0] for n in g.nodes(data=True) if 'bot' in n[1]['roles'] ]

# %%
nx_cluster.triangles(g, 0)
# %%
aG = g.subgraph(sysop)
aGComp = list(nx_comp.connected_components(aG))
aGConnected = g.subgraph([c for c in aGComp if len(c) > 1][0])
# %%
pos = nx.spring_layout(aG, k=0.1)
plt.rcParams.update({'figure.figsize': (50, 30)})
nx.draw_networkx(
    aG,
    pos=pos,
    node_size=1,
    edge_color="#990000",
    alpha=0.05,
    with_labels=False)
# %%
