import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 100000); q = sc(k, 100000)
    cur = rng.sample(range(1, 10**9), n); used = set(cur); lst = list(cur); cmds = []
    for _ in range(q):
        if lst and rng.random() < 0.4:
            i = rng.randrange(len(lst)); x = lst[i]; lst[i] = lst[-1]; lst.pop()
            cmds.append('remove %d' % x)
        elif lst:
            x = rng.choice(lst); y = rng.randint(1, 10**9)
            while y in used: y = rng.randint(1, 10**9)
            used.add(y); lst.append(y)
            cmds.append('%s %d %d' % (rng.choice(['after', 'before']), x, y))
    return '%d\n%s\n%d\n%s\n' % (n, ' '.join(map(str, cur)), len(cmds), '\n'.join(cmds))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1606 * 100 + t), t))
