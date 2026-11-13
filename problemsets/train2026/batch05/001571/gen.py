import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    tot = sc(k, 200000); m = rng.randint(1, min(10000, max(1, tot // 2)))
    hi = rng.choice([5, 10**9])
    cnt = [0] * m
    for _ in range(tot): cnt[rng.randrange(m)] += 1
    ls = []
    for c in cnt:
        ls.append('%d %s' % (c, ' '.join(map(str, sorted(rng.randint(-hi, hi) for _ in range(c))))))
    return '%d\n%s\n' % (m, '\n'.join(x.strip() for x in ls))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1571 * 100 + t), t))
