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

def query(username, cont):
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'usercontribs',
        'ucuser': username,
        'ucnamespace': 0,
        'ucstart': '2008-01-07T00:00:00Z',
        'uclimit': 500,	
    }
    pbarReq.update(1)
    if cont:
        params['uccontinue'] = cont
    return session.get(url=BASE_URL, params=params).json()

def getContributions(username):
    contrib = []
    cont = False

    while True:
        res = query(username, cont)
        if 'query' in res and 'usercontribs' in res['query']:
            contrib += res['query']['usercontribs']

        if 'continue' in res and 'uccontinue' in res['continue']:
            cont = res['continue']['uccontinue']
        else:
            break

    contrib.sort(key=lambda x: x['timestamp'])
    return contrib

def saveToFile(id, username, contrib, f: TextIOWrapper):
    f.write(f'{id}\t{username}\n')
    for c in contrib:
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
    for id, username in lines:

        cont = getContributions(username)
        saveToFile(id, username, cont, out)
        pbar.update(1)

with open(f'contrib/contrib-{str(fr).zfill(7)}-{str(to).zfill(7)}.done.txt', 'w') as out:
        out.write(f'Done contrib-{str(fr).zfill(7)}-{str(to).zfill(7)}.txt\n')
with open('contrib/done.txt', 'a') as out:
        out.write(f'{str(fr).zfill(7)}-{str(to).zfill(7)}\n')


pbar.close()
pbarReq.close()
print('Done')


#  %%
n = 5000
ii = 0
with open('run.sh', 'w') as f:
    for i in range(0, 1140148, n):
        f.write(f'tmux new-session -d -s "{ii}" &&')
        f.write(f'tmux send -t "{ii}" "python ./dossing-wikipedia.py {i} {i+n}" Enter &&\n')
        ii += 1

# %%
