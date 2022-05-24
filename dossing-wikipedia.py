#  %%
from io import TextIOWrapper
import requests
import sys
from tqdm import tqdm
BASE_URL = 'https://en.wikipedia.org/w/api.php'
session = requests.Session()


# %% functions
def getNamesAndIds(f: TextIOWrapper, n: int):
    names = []
    ids = []
    for line in f:
        line = line.strip()
        if line:
            id, name = line.split('\t')
            names.append(name)
            ids.append(id)
    return names, ids

def query(names, cont):
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'usercontribs',
        'ucuser': '|'.join(names),
        'ucnamespace': 0,
        'ucstart': '2008-01-07T00:00:00Z',
        'uclimit': 500,	
    }
    pbarReq.update(1)
    if cont:
        params['uccontinue'] = cont
    return session.get(url=BASE_URL, params=params).json()

def getContributions(users):
    contrib = []
    cont = False
    while True:
        res = query(users, cont)
        if 'query' in res and 'usercontribs' in res['query']:
            contrib += res['query']['usercontribs']
        if 'continue' in res and 'uccontinue' in res['continue']:
            cont = res['continue']['uccontinue']
        else:
            break
    contrib.sort(key=lambda x: x['timestamp'])
    return contrib

def saveToFile(ids, usernames, contrib, f: TextIOWrapper):
    contDic = {}
    for u in usernames:
        contDic[u] = []
    for c in contrib:
        contDic[c['user'].replace(' ', '_') ].append(c)


    for id, u in zip(ids, usernames):
        f.write(f'{id}\t{u}\n')
        for c in contDic[u]:
            f.write('\t'.join([ str(c['pageid']), c['title'], c['timestamp'], str(c['revid']) ]) + '\n')
        f.write('\n')






#  %%
fr = int(sys.argv[1])
to = int(sys.argv[2])

pbarReq = tqdm(position=0)
pbar = tqdm(total=to-fr, position=1)

n = 1

with open('dataset/usernames.txt') as f:
    lines = [ l.strip().split(' ') for l in list(f)[fr:to] ]

with open(f'contrib/contrib-{str(fr).zfill(7)}-{str(to).zfill(7)}.txt', 'w') as out:
    setsOfLines = [lines[i:i + n] for i in range(0, len(lines), n)]

    for s in setsOfLines:
        ids = [ l[0] for l in s ]
        names = [ l[1] for l in s ]

        cont = getContributions(names)
        saveToFile(ids, names, cont, out)

        pbar.update(len(names))

        out.write(f'Done contrib-{str(fr).zfill(7)}-{str(to).zfill(7)}.txt\n')

pbar.close()
pbarReq.close()
print('Done')


#  %%
# n = 5000
# with open('run.sh', 'w') as f:
#     for i in range(0, 1140148, n):
#         f.write(f'tmux new-session -d -s "{i}" python ./dossing-wikipedia.py {i} {i+n} &&\n')

# %%
