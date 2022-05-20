# %%
import bz2
from tqdm import tqdm

# %%
with bz2.open('out.txt.bz2', 'wt') as out:
    toPrint = True
    i = 0
    with bz2.open("dataset/enwiki-20080103.main.bz2", "rt") as f:
        for line in tqdm(f):
            if i == 0:
                info = line.strip().split(' ')
                out.write(f'{info[1]}\t{info[3]}\t{info[6]}\t{info[5]}\n')
                toPrint = False
                i = 14
            i -= 1
print('DONE')
# %%
