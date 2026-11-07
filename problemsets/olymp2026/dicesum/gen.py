"""gen.py n maxFaces maxValue q seed (the totals are capped at 2e5)"""
import random
import sys

n, F, V, q, s = (int(x) for x in sys.argv[1:6])
random.seed(s * 1201 + n)
dice = []
tot_k = tot_v = 0
for i in range(n):
    left = n - i - 1
    k = random.randint(1, F)
    k = min(k, 200000 - tot_k - left)
    mv = random.randint(0, V) if random.random() < 0.8 else V
    mv = max(0, min(mv, 200000 - tot_v))
    faces = [random.randint(0, mv) for _ in range(k)]
    if random.random() < 0.3:
        faces = [random.choice(faces[:3]) for _ in range(k)]  # repeated values
    tot_k += k
    tot_v += max(faces)
    dice.append(faces)
S = tot_v
lines = ['%d %d' % (n, q)] + ['%d %s' % (len(f), ' '.join(map(str, f))) for f in dice]
for _ in range(q):
    r = random.random()
    if r < 0.7:
        mid = S // 2 + int(random.gauss(0, max(1, S ** 0.5)))
        a, b = mid, mid + random.randint(0, max(1, int(S ** 0.5)))
    elif r < 0.9:
        a, b = random.randint(0, S + 2), random.randint(0, S + 2)
    else:
        a, b = random.randint(0, 10 ** 9), random.randint(0, 10 ** 9)
    a, b = max(0, min(a, b)), max(0, max(a, b))
    lines.append('%d %d' % (a, min(b, 10 ** 9)))
print('\n'.join(lines))
