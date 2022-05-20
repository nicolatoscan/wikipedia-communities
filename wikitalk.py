# %% imports
from random import seed
from typing import Counter
import networkx as nx
import networkx.algorithms.community as nx_comm
import networkx.algorithms.smallworld as nx_sw
import networkx.algorithms.components as nx_comp
import networkx.algorithms.cluster as nx_cluster
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Pool
import numpy as np
import json
cores = 12

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


print('Getting usernames...')
usernames = {}
idToUsername = {}
with open('dataset/usernames.txt', 'r') as f:
    for line in tqdm(f):
        id, username = line.strip('\n').split(' ')
        usernames[username] = int(id)
        idToUsername[int(id)] = username

print('Adding computed users info ... ')
with open('dataset/users.json', 'r') as f:
    users = json.load(f)
    for id in tqdm(users):
        count, fr, to = users[id]
        iid = int(id)
        g.nodes[iid]['count'] = count
        g.nodes[iid]['from'] = fr
        g.nodes[iid]['to'] = to
        g.nodes[iid]['total'] = to - fr
        g.nodes[iid]['freq'] = (to - fr) / count

print('Adding props...')
genderMap = { 'female': 1, 'male': 0, 'unknown': -1 }
with open('dataset/userinfo.tsv', 'r') as f:
    for line in tqdm(f):
        data = line.strip('\n').split('\t')
        if len(data) == 6:
            id, name, gender, editcount, firstedit, roles = line.strip('\n').split('\t')
            if name in usernames:
                id = usernames[name]
                g.nodes[id]['id'] = id
                g.nodes[id]['name'] = name
                g.nodes[id]['gender'] = genderMap[gender]
                g.nodes[id]['roles'] = roles.split(',')

print('Fix missing...')
for id in tqdm(g.nodes):
    if 'id' not in g.nodes[id]:
        g.nodes[id]['id'] = -1
        g.nodes[id]['name'] = idToUsername[id]
        g.nodes[id]['gender'] = -1
        g.nodes[id]['roles'] = [ '*' ]
    if 'count' not in g.nodes[id]:
        g.nodes[id]['count'] = 0
        g.nodes[id]['from'] = -1
        g.nodes[id]['to'] = -1
        g.nodes[id]['total'] = 0
        g.nodes[id]['freq'] = 0

# %% count roles
roles = Counter()
for n in g.nodes(data=True):
    roles.update(n[1]['roles'])
df = pd.DataFrame.from_dict(roles, orient='index').reset_index()
print(df)

# %% different graphs indexing
gIndex = {
    'All': 0,
    'Autoconfirmed': 1,
    'ExtendedConfirmed': 2,
    'Sysop': 3,
    'Male': 4,
    'Female': 5,
}
ii = list(gIndex.keys())

# %% groups
def getRoleGraph(g, role: str | int, isGender: bool) -> nx.Graph:
    if isGender:
        subG = g.subgraph([ n[0] for n in g.nodes(data=True) if role == n[1]['gender'] ])
    else:
        subG = g.subgraph([ n[0] for n in g.nodes(data=True) if role in n[1]['roles'] ])

    comp = list(nx_comp.connected_components(subG))
    comp10 = [ c for c in comp if len(c) > 10 ]
    print(f'Nr comp {role}: {len(comp10)}')
    return subG.subgraph(comp10[0])


gAll = getRoleGraph(g, '*', False)
gAC = getRoleGraph(g, 'autoconfirmed', False)
gACX = getRoleGraph(g, 'extendedconfirmed', False)
gSYS = getRoleGraph(g, 'sysop', False)

gM = getRoleGraph(g, genderMap['male'], True)
gF = getRoleGraph(g, genderMap['female'], True)

subG = [ gAll, gAC, gACX, gSYS, gM, gF ]

dfNandE = pd.DataFrame(
    columns=['Nodes', 'Edges'], index=ii,
    data=[ [len(gg.nodes()), len(gg.edges())] for gg in tqdm(subG) ],
)
print(dfNandE)

# %% comm detection
# pool = Pool(processes=cores)
# comms = pool.imap_unordered(nx_comm.louvain_communities, [gAC, gACX, gSYS, gM, gF])
comms = [ nx_comm.louvain_communities(gg, seed=42) for gg in tqdm([ gAll, gAC, gACX, gSYS, gM, gF ]) ]
[ comm, commAC, commACX, commSYS, commM, commF ] = comms
comms10 = [ [ c for c in com if len(c) > 5 ] for com in comms ]
comms5 = [ [ c for c in com if len(c) > 5 ] for com in comms ]

# %%
def commsInfo(ccc):
    res = pd.DataFrame(
        columns=['Total', 'Nr comms', 'Median', 'Avg size', 'std'], index=ii,
        data=[ [ 
            int(np.sum([ len(c) for c in cc ])),
            len(cc),
            int(np.median([ len(c) for c in cc ])),
            int(np.average([ len(c) for c in cc ])),
            int(np.std([ len(c) for c in cc ])),
        ] for cc in tqdm(ccc) ],
    )
    print(res)
print('All')
commsInfo(comms)
print('Less than 5 removed')
commsInfo(comms5)
print('Less than 10 removed')
commsInfo(comms10)
# %% removing comms with less than 10 nodes

# %%
