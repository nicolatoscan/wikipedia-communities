# %%
from typing import Counter
from tqdm import tqdm

# %%
# PAGE NAMES DICTIONARE
print('PAGE NAMES DICTIONARE')
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
print('Done!\n')

# %%
# PAGE ID TO TOPCAT
print('PAGE ID TO TOPCAT')
pageIdToTopcat = {}
with open('dataset/wiki-topcats-categories.txt') as f:
    for l in tqdm(f):
        name, ids = l.strip().split(';')
        name = name.strip('Category:')
        ids = [ int(id) for id in ids.strip().split(' ') if id ]
        for id in ids:
            pageIdToTopcat[id] = name
print('Done!\n')

# %%
# join files
# print('JOIN FILES')
# with open('contrib/contributions.csv', 'w') as out:
#     for i in tqdm(
#         list(range(0, 15000, 500)) +
#         list(range(15000, 1140150, 5000))
#     ):
#         with open(f'done/contrib-{str(i).zfill(7)}.txt') as f:
#             for l in f:
#                 out.write(l)
# print('Done!\n')

# %%
# generate csv
print('USERS CONTRIBUTIONS DONE')
with tqdm(desc='Generating csv') as pBar:
    with open('contrib/users-contributions.csv', 'w') as out:
        with open('contrib/contributions.csv') as f:
            line = f.readline()
            while line:
                id, username = line.strip().split('\t')
                pageNames = []
                pageIds = []

                line = f.readline().strip()
                while line:
                    pageId, pageName, time, revId = line.split('\t')
                    pageIds.append(pageId)
                    pageNames.append(pageName)
                    line = f.readline().strip()

                topcatPagesIds = [ pageNameToId[p] for p in pageNames if p in pageNameToId ]
                # topcatNames = [ pageIdToTopcat[id] for id in topcatPagesId ]

                pageIdsCounter = Counter(pageIds)
                topcatPagesIdsCounter = Counter(topcatPagesIds)

                userInfo = '\t'.join([ 
                    id, username,
                    "|".join([ f'{p[0]},{p[1]}' for p in topcatPagesIdsCounter.most_common() ]),
                    "|".join([ f'{p[0]},{p[1]}' for p in pageIdsCounter.most_common() ]),
                ])
                out.write(f'{userInfo}\n')

                pBar.update(1)
                line = f.readline()
print('Done!\n')
print('ALL DONE')

# %%
