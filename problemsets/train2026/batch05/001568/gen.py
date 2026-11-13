import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    q = sc(k, 200000)
    cmds = []
    for _ in range(q):
        c = rng.choice(['push_front', 'push_back', 'push_front', 'push_back', 'pop_front', 'pop_back', 'front', 'back', 'size'])
        cmds.append(c + (' %d' % rng.randint(-10**9, 10**9) if c.startswith('push') else ''))
    return '%d\n%s\n' % (q, '\n'.join(cmds))

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1568 * 100 + t), t))
