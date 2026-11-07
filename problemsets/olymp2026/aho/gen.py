"""gen.py sigma k L maxLen seed (total length capped at 100)"""
import random
import sys

sigma, k, L, ML, s = (int(x) for x in sys.argv[1:6])
random.seed(s * 9103 + k)
letters = 'abcdefghijklmnopqrstuvwxyz'[:sigma]
words, total = [], 0
base = ''.join(random.choice(letters) for _ in range(200))
for i in range(k):
    left = 100 - total - (k - i - 1)
    ln = max(1, min(random.randint(1, ML), left))
    if random.random() < 0.4:  # overlapping words taken from one random text
        st = random.randint(0, 200 - ln)
        w = base[st:st + ln]
    else:
        w = ''.join(random.choice(letters) for _ in range(ln))
    words.append(w)
    total += ln
print(sigma, k, L)
print('\n'.join(words))
