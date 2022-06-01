#  %%
from ctypes import cast
import enum
from io import TextIOWrapper
import sys
import requests
from tqdm import tqdm
from multiprocessing import Pool
from joblib import Parallel, delayed
from blessings import Terminal
import time
BASE_URL = 'https://en.wikipedia.org/w/api.php'
session = requests.Session()

done = []

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

def query(username, cont, fr):
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'usercontribs',
        'ucuser': username,
        'ucnamespace': 0,
        'ucstart': '2008-01-07T00:00:00Z',
        'uclimit': 500,	
    }
    # pbarReq.update(1)
    if cont:
        params['uccontinue'] = cont
    res = None
    tried = 0
    while res is None and tried < 5:
        tried += 1
        try:
            res = session.get(BASE_URL, params=params).json()
        except:
            pass
    if res is None:
        with open('diocane.log', 'a') as out:
            out.write(f'{username} from {fr}\n')
    return res

def getContributions(username, fr):
    contrib = []
    cont = False

    while True:
        res = query(username, cont, fr)
        if res is None:
            break

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


def run(params):
    counter, (i, lines) = params
    if i in done:
        return
    pbar = tqdm(total=len(lines), position=counter, desc=f'Processo {counter}')

    with open(f'contrib/contrib-{str(i).zfill(7)}.txt', 'w') as out:
        for id, username in lines:

            cont = getContributions(username, i)
            saveToFile(id, username, cont, out)
            pbar.update(1)
            # pbarTotal.update(1)
        # pbarFiles.update(1)


    with open(f'contrib/contrib-{str(i).zfill(7)}.done.txt', 'w') as out:
        out.write(f'Done contrib/contrib-{str(i).zfill(7)}.txt\n')
    with open('contrib/done.txt', 'a') as out:
        out.write(f'{str(i).zfill(7)}\n')


    # pbar.close()
    # pbarTotal.close()
    # pbarFiles.close()


# %% read files
lines = []
with open('dataset/usernames.txt') as f:
    lines = [ l.strip().split(' ') for l in list(f) ]

# %% group inputs
n = 500
inputs = []
for i in range(0, 1140150, n):
    inputs.append((i, lines[i:i+n]))

#  %%
# try:
#     fr = int(sys.argv[1])
#     to = int(sys.argv[2])
# except:
#     fr = 0
#     to = 10

# pbarTotal = tqdm(position=0, total=sum([ len(inp) for inp in inputs[fr:to] ]), desc='Total')
# pbarFiles = tqdm(position=1, total=to-fr, desc='Files')
# %%
pool = Pool(processes=100)
for i in range(0, 30, 10):
    fr = i
    to = i+10
    print(f'Processing {len(inputs[fr:to])} processes from {fr} to {to} of {len(inputs)}')
    pool.map(run, enumerate(inputs[fr:to]))
#  %%
# Parallel(n_jobs=100)(delayed(run)(i) for i in enumerate(inputs[fr:to]))

#  %%
# n = 5000
# ii = 0
# with open('run.sh', 'w') as f:
#     for i in range(0, 1140148, n):
#         f.write(f'tmux new-session -d -s "{ii}" && ')
#         f.write(f'tmux send -t "{ii}" "python ./dossing-wikipedia.py {i} {i+n}" Enter &&\n')
#         ii += 1

# %%
