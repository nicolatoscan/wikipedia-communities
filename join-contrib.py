# %%
from tqdm import tqdm
# %%
n = 5000
with open('contrib/contributions.csv', 'w') as out:
    for i in tqdm(range(15000, 1140150, n)):
        if i == 410000: continue
        with open(f'done/contrib-{str(i).zfill(7)}.txt') as f:
            for l in f:
                out.write(l)

# %%
# PAGE NAMES DICTIONARE
pageNameToId = {}
skipped = 0
with open('dataset/wiki-topcats-page-names.txt') as f:
    for l in tqdm(f):
        infos = l.strip().split(' ', 1)
        if len(infos) == 2:
            pageNameToId[infos[1]] = int(infos[0])
        else:
            skipped += 1
print(f'Skipped {skipped} lines')

# %%
# PAGE ID TO TOPCAT
pageIdToTopcat = {}
with open('dataset/wiki-topcats-categories.txt') as f:
    for l in tqdm(f):
        name, ids = l.strip().split(';')
        name = name.strip('Category:')
        ids = [ int(id) for id in ids.strip().split(' ') if id ]
        for id in ids:
            pageIdToTopcat[id] = name
print(f'Done')

# %%
with tqdm(desc='Generating csv') as pBar:
    with open('contrib/users-contributions.csv', 'w') as out:
        with open('contrib/contributions.csv') as f:
            line = f.readline()
            while line:
                id, username = line.strip().split('\t')
                pageNames = set()
                pageIds = set()

                line = f.readline().strip()
                while line:
                    pageId, pageName, time, revId = line.split('\t')
                    pageNames.add(pageName)
                    pageIds.add(pageId)
                    
                    line = f.readline().strip()

                topcatPagesId = [ pageNameToId[p] for p in pageNames if p in pageNameToId ]
                topcatNames = set([ pageIdToTopcat[id] for id in topcatPagesId ])
                userInfo = '\t'.join([ 
                    id, username,
                    "|".join(pageNames),
                    "|".join(pageIds),
                    "|".join([str(id) for id in topcatPagesId ]),
                    "|".join(topcatNames)
                ])
                out.write(f'{userInfo}\n')

                pBar.update(1)
                line = f.readline()
print('Done')


# %%
