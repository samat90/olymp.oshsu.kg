"""gen.py n q sigma mode(rand/periodic/fib/text/runs) kmode(any/small/big) seed"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genlib import seed, write  # noqa: E402

n, q, sigma = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
mode, kmode, s = sys.argv[4], sys.argv[5], sys.argv[6]
seed(s)
letters = 'abcdefghijklmnopqrstuvwxyz'[:sigma]
# words of the epos in Latin transliteration, used for 'text'
WORDS = ['manas', 'semetey', 'seytek', 'kanykey', 'almambet', 'bakay', 'chubak', 'syrgak', 'akkula', 'talas',
         'jakyp', 'chyiyrdy', 'koshoy', 'er', 'baatyr', 'kyrgyz', 'el', 'jurt', 'ala', 'too', 'kol', 'ordo']
if mode == 'periodic':
    base = ''.join(random.choice(letters) for _ in range(random.randint(1, 30)))
    t = (base * (n // len(base) + 1))[:n]
    t = list(t)
    for _ in range(random.randint(0, 3)):
        t[random.randrange(n)] = random.choice(letters)
    t = ''.join(t)
elif mode == 'fib':
    a, b = 'a', 'ab' if sigma > 1 else 'aa'
    while len(b) < n:
        a, b = b, b + a
    t = b[:n]
elif mode == 'text':
    parts = []
    while sum(map(len, parts)) < n:
        parts.append(random.choice(WORDS))
    t = ''.join(parts)[:n]
elif mode == 'runs':
    t = ''
    while len(t) < n:
        t += random.choice(letters) * random.randint(1, 5000)
    t = t[:n]
else:
    t = ''.join(random.choice(letters) for _ in range(n))


def distinct(t):
    """Number of distinct substrings (suffix automaton)."""
    nxt, link, length = [{}], [-1], [0]
    last = 0
    for ch in t:
        cur = len(length)
        nxt.append({}); link.append(0); length.append(length[last] + 1)
        p = last
        while p != -1 and ch not in nxt[p]:
            nxt[p][ch] = cur
            p = link[p]
        if p != -1:
            q = nxt[p][ch]
            if length[p] + 1 == length[q]:
                link[cur] = q
            else:
                cl = len(length)
                nxt.append(dict(nxt[q])); link.append(link[q]); length.append(length[p] + 1)
                while p != -1 and nxt[p].get(ch) == q:
                    nxt[p][ch] = cl
                    p = link[p]
                link[q] = link[cur] = cl
        last = cur
    return sum(length[v] - length[link[v]] for v in range(1, len(length)))


total = distinct(t)
ks = []
for _ in range(q):
    c = random.random()
    if kmode == 'small':
        ks.append(random.randint(1, min(total, 1000)))
    elif kmode == 'big' or c < 0.1:
        ks.append(random.choice([total, total + 1, random.randint(total // 2, total), 10 ** 12]))
    else:
        ks.append(random.randint(1, max(1, total // random.choice([1, 2, 10, 1000]))))
write(['%d %d' % (n, q), t, ' '.join(map(str, ks))])
