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
from IPython.display import display
import math
cores = 12

# %% graph
g = nx.Graph()
# g = nx.DiGraph()
# g = nx.MultiDiGraph()

print('Mapping id to usernams...')
usernames = {}
idToUsername = {}
with open('dataset/usernames.txt', 'r') as f:
    for line in tqdm(f):
        id, username = line.strip('\n').split(' ')
        usernames[username] = int(id)
        idToUsername[int(id)] = username

userinfo = {}
emptyUserinfo = {
    'id': -1, 'name': '', 'gender': -1, 'roles': ['*'],
    'count': 0, 'from': -1, 'to': -1, 'total': 0, 'freq': 0, 'active': False
}

print("Getting API users information")
genderMap = { 'female': 1, 'male': 0, 'unknown': -1 }
with open('dataset/userinfo.tsv', 'r') as f:
    for line in tqdm(f):
        data = line.strip('\n').split('\t')
        if len(data) == 6:
            wikiid, name, gender, editcount, firstedit, roles = line.strip('\n').split('\t')
            if name in usernames:
                id = usernames[name]
                userinfo[id] = {
                    'id': wikiid,
                    'name': name,
                    'gender': genderMap[gender],
                    'roles': roles.split(','),
                    'count': 0, 'from': -1, 'to': -1, 'total': 0, 'freq': 0, 'active': False
                }

print("Getting calculated users information")
with open('dataset/users.json', 'r') as f:
    users = json.load(f)
    for id in tqdm(users):
        count, fr, to = users[id]
        iid = int(id)
        if iid not in userinfo:
            userinfo[iid] = {'id': -1, 'name': id, 'gender': -1, 'roles': ['*'] }
        userinfo[iid]['count'] = count
        userinfo[iid]['from'] = fr
        userinfo[iid]['to'] = to
        userinfo[iid]['active'] = to > 1191838728
        userinfo[iid]['total'] = to - fr
        userinfo[iid]['freq'] = (to - fr) / count

bots = []
with open('dataset/wikitalk.txt', 'r') as f:
    print('Importing data...')
    data =  [ list(map(int, line.strip().split(' '))) for line in tqdm(list(f)) ]

    print('Adding nodes ...')
    nodes = set([item for sublist in data for item in sublist[0:2]])
    for n in tqdm(nodes):
        uInfo = userinfo[n] if n in userinfo else emptyUserinfo
        g.add_node(n, **uInfo)

    print('Adding edges...')
    edges = {}
    for info in tqdm(data):
        
        senderRoles = userinfo[info[0]]['roles']
        w = 1
        if 'autoconfirmed' in senderRoles: w = 4
        if 'extendedconfirmed' in senderRoles: w = 72
        if 'sysop' in senderRoles: w = 1584

        if (info[0], info[1]) not in edges:
            edges[(info[0], info[1])] = {
                'weight': w, 'first': info[2], 'last': info[2],
            }
        else:
            edges[(info[0], info[1])]['weight'] += w
            edges[(info[0], info[1])]['last'] = max(edges[(info[0], info[1])]['last'], info[2])
            edges[(info[0], info[1])]['first'] = min(edges[(info[0], info[1])]['first'], info[2])

    for e in tqdm(edges):
        g.add_edge(e[0], e[1], **edges[e])

    print("Removing bots")
    g.remove_nodes_from([ n[0] for n in g.nodes(data=True) if 'bot' in n[1]['roles'] ])

    del data
    del nodes
    del edges
    print('Done!')


# %% count roles
roles = Counter()
for n in g.nodes(data=True):
    roles.update(n[1]['roles'])
rolesDf = pd.DataFrame.from_dict(roles, orient='index').reset_index()
rolesDf['ratio'] = len(g.nodes(data=True)) / rolesDf[0]
display(rolesDf.round())

# %% groups
gIndex = {
    'Autoconfirmed': 1,
    'ExtendedConfirmed': 2,
    'Sysop': 3,
    'Male': 4,
    'Female': 5,
}
ii = list(gIndex.keys())

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

subG = [ gAC, gACX, gSYS, gM, gF ]

dfNandE = pd.DataFrame(
    columns=['Nodes', 'Edges'], index=ii,
    data=[ [len(gg.nodes()), len(gg.edges())] for gg in tqdm(subG) ],
)
display(dfNandE)

# %% comm detection
# pool = Pool(processes=cores)
# comms = pool.imap_unordered(nx_comm.louvain_communities, [gAC, gACX, gSYS, gM, gF])
# comms = [ nx_comm.louvain_communities(gg, seed=42) for gg in tqdm(subG) ]
# [ comm, commAC, commACX, commSYS, commM, commF ] = comms
# comms10 = [ [ c for c in com if len(c) > 5 ] for com in comms ]
# comms5 = [ [ c for c in com if len(c) > 5 ] for com in comms ]

# %%
def commsInfo(ccc, graphs):
    res = pd.DataFrame(
        columns=['Total', 'Nr comms', 'Median', 'Avg size', 'std',
            'Modularity', 'PQ'
        ], index=ii,
        data=[ [
            int(np.sum([ len(c) for c in cc ])),
            len(cc),
            int(np.median([ len(c) for c in cc ])),
            int(np.average([ len(c) for c in cc ])),
            int(np.std([ len(c) for c in cc ])),
            nx_comm.modularity(gg, cc),
            nx_comm.partition_quality(gg, cc)
        ] for cc, gg in tqdm(list(zip(ccc, graphs))) ],
    )
    res[['Coverage', 'Perfermance']] = pd.DataFrame(res['PQ'].tolist(), index=res.index)
    res.drop(['PQ'], axis=1, inplace=True)
    display(res.round(2))

def commAndPrint(name, graphs, resolution):
    print(name)
    communities = [ nx_comm.louvain_communities(gg, seed=42, resolution=resolution) for gg in tqdm(graphs) ]
    commsInfo(communities, graphs)
    return communities


# %% all
comms = commAndPrint('All', subG, 1)
# %% R 0.75
commsRP75 = commAndPrint('0.75', subG, 0.75)
# %% R 2
commsR2 = commAndPrint('2', subG, 2)

# %%
comms10 = [ [ c for c in com if len(c) > 5 ] for com in comms ]
comms5 = [ [ c for c in com if len(c) > 5 ] for com in comms ]


# %% size distribution
def plotSizeDistribution(communities):
    fig, ax = plt.subplots(3,1, figsize=(10,10))
    titles = ['Autoconfirmed', 'Extended AC', 'Admins']
    colors = ['b', 'r', 'g']
    for i in range(3):
        ax[i].set_title(titles[i])
        ax[i].hist([ len(c) for c in communities[i] ], 50, facecolor=colors[i], alpha=0.75)
        ax[i].grid(True)
        ax[i].set_ylabel('Density')
        if i == 2:
            ax[i].set_xlabel('Number of nodes in community')

plotSizeDistribution(comms)

# %%
def plotGenderDistribution(communities, title):
    genderInComms = []
    for c in tqdm(communities):
        cGraph = g.subgraph(c)
        nrFema = sum([ 1 for n in cGraph.nodes(data=True) if n[1]['gender'] ==  1 ])
        nrMale = sum([ 1 for n in cGraph.nodes(data=True) if n[1]['gender'] ==  0 ])
        nrUnkn = sum([ 1 for n in cGraph.nodes(data=True) if n[1]['gender'] == -1 ])
        nrAll = nrFema + nrMale + nrUnkn
        nrKnown = nrFema + nrMale
        if nrKnown > 0:
            genderInComms.append([ 
                nrMale / nrKnown,
                nrFema / nrKnown,
                nrKnown / nrAll,
            ])

    fig, ax = plt.subplots(3,1, figsize=(10,10))
    fig.suptitle(title, fontsize=16)
    titles = ['Male', 'Female', 'Known']
    colors = ['b', 'r', 'g']
    for i in range(3):
        ax[i].set_title(titles[i])
        ax[i].hist([x[i] for x in genderInComms], 50, facecolor=colors[i], alpha=0.75)
        ax[i].grid(True)

    plt.show()


def plotActivnessDistribution(communities):
    frequensies = []
    for c in tqdm(communities):
        cGraph = g.subgraph(c)
        freqList = [ n[1]['freq'] for n in cGraph.nodes(data=True) ]
        frequensies.append(np.average(freqList))

    plt.hist(frequensies, 50)
    plt.show()

# %% hist R1
plotGenderDistribution(comms[0], 'Autoconfirmed')
plotGenderDistribution(comms[1], 'extended autoconfirmed')
plotGenderDistribution(comms[2], 'Admins')

# %% hist R0.75
plotGenderDistribution(commsRP75[0], 'Autoconfirmed 0.75')
plotGenderDistribution(commsRP75[1], 'extended autoconfirmed 0.75')
plotGenderDistribution(commsRP75[2], 'Admins 0.75')

# %% hist R2
plotGenderDistribution(commsR2[0], 'Autoconfirmed 2')
plotGenderDistribution(commsR2[1], 'extended autoconfirmed 2')
plotGenderDistribution(commsR2[2], 'Admins 2')
# %%
plotActivnessDistribution(comms[1])
# %% correlations
def correlationMatrix(communities):
    cols = ['freq', 'total', 'count', 'size', 'Male', 'Female', 'Known']
    info = []
    for c in communities:
        cGraph = g.subgraph(c)
        freq = np.average([ n[1]['freq'] for n in cGraph.nodes(data=True) ])
        total = np.average([ n[1]['total'] for n in cGraph.nodes(data=True) ])
        count = np.average([ n[1]['count'] for n in cGraph.nodes(data=True) ])
        size = np.sum([ 1 for n in cGraph.nodes(data=True) ])
        nrFema = sum([ 1 for n in cGraph.nodes(data=True) if n[1]['gender'] ==  1 ])
        nrMale = sum([ 1 for n in cGraph.nodes(data=True) if n[1]['gender'] ==  0 ])
        nrUnkn = sum([ 1 for n in cGraph.nodes(data=True) if n[1]['gender'] == -1 ])
        nrAll = nrFema + nrMale + nrUnkn
        nrKnown = nrFema + nrMale

        info.append([
            freq,
            total,
            count,
            size,
            nrMale / nrKnown if nrKnown > 0 else 0,
            nrFema / nrKnown if nrKnown > 0 else 0,
            nrKnown / nrAll
        ])

    dfCorr = pd.DataFrame(info, columns=cols).corr()
    display(dfCorr.style.background_gradient())

print('Autoconfirmed')
correlationMatrix(comms[0])
print('extended autoconfirmed')
correlationMatrix(comms[1])
print('Admins')
correlationMatrix(comms[2])

# %% plot property
def histProperty(communitieses, prop):
    toHists = []
    for i in range(3):
        toHists.append([
            np.average([ n[1][prop] for n in  g.subgraph(c).nodes(data=True) ])
            for c in communitieses[i]
            if len(c) > 2
        ])

    fig, ax = plt.subplots(3,1, figsize=(10,10))
    fig.suptitle(prop, fontsize=16)
    titles = ['AC', 'ACX', 'Admins']
    colors = ['b', 'r', 'g']
    for i in range(3):
        ax[i].set_title(titles[i])
        ax[i].hist(toHists[i], 50, facecolor=colors[i], alpha=0.75)
        ax[i].grid(True)

    plt.show()

histProperty(comms, 'freq')
histProperty(comms, 'count')
histProperty(comms, 'total')
histProperty(comms, 'active')
# %%
emptyUserinfo = {
    'id': -1, 'name': '', 'gender': -1, 'roles': ['*'],
    'count': 0, 'from': -1, 'to': -1, 'total': 0, 'freq': 0, 'active': False
}
# %%
