"""gen.py m P seed: m distinct chords between nails 1..P (P small: many shared nails)"""
import random
import sys

m, P, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
random.seed(s * 6151 + m)
P = max(P, 2)
mode = random.choice(['rand', 'short', 'long', 'star'])
seen = set()
out = []
limit = P * (P - 1) // 2
m = min(m, limit)
hub = random.randint(1, P)
tries = 0
while len(out) < m:
    tries += 1
    if tries > 20 * m + 1000:
        mode = 'rand'
    if mode == 'short':
        a = random.randint(1, P)
        b = a + random.randint(1, max(1, min(P - 1, P // 50 + 2)))
        if b > P:
            continue
    elif mode == 'long':
        a = random.randint(1, max(1, P // 3))
        b = random.randint(min(P, 2 * P // 3 + 1), P)
    elif mode == 'star' and random.random() < 0.3:
        a, b = hub, random.randint(1, P)
    else:
        a, b = random.randint(1, P), random.randint(1, P)
    if a == b:
        continue
    key = (min(a, b), max(a, b))
    if key in seen:
        continue
    seen.add(key)
    out.append((a, b) if random.random() < 0.5 else (b, a))
print(len(out))
print('\n'.join('%d %d' % q for q in out))
