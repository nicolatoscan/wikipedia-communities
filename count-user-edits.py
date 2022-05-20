# %%
from tqdm import tqdm
import json

# %%
users = {}

counter = 0
first = 1
last = 2

with open('dataset/wikitalk.txt', 'r') as f:
    for line in tqdm(f):
        fr, to, time = [ int(x) for x in line.strip('\n').split(' ')]
        if fr not in users:
            users[fr] = [1, time, time]
        else:
            users[fr][0] += 1
            users[fr][1] = min(users[fr][1], time)
            users[fr][2] = max(users[fr][2], time)
# %%
with open('dataset/users.json', 'w') as f:
    json.dump(users, f)
# %%
