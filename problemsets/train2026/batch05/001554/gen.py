import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def gen(rng, k):
    n = sc(k, 100000)
    a = rng.choice(['abc', 'abcd', 'abcdefghijklmnopqrstuvwxyz'])
    return ''.join(rng.choice(a) for _ in range(n)) + '\n'

if __name__ == "__main__":
    t = int(sys.argv[1])
    sys.stdout.write(gen(random.Random(1554 * 100 + t), t))
