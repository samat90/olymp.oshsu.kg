# Independent check: Grundy values by memoised DFS and counting with dictionaries.
import sys
from collections import Counter
def main():
    d = sys.stdin.buffer.read().split()
    n, m = int(d[0]), int(d[1])
    adj = [[] for _ in range(n + 1)]
    p = 2
    for _ in range(m):
        adj[int(d[p])].append(int(d[p + 1])); p += 2
    g = [-1] * (n + 1)
    for s in range(1, n + 1):
        if g[s] >= 0:
            continue
        stack = [(s, 0)]
        while stack:
            v, i = stack.pop()
            if i < len(adj[v]):
                stack.append((v, i + 1))
                u = adj[v][i]
                if g[u] < 0:
                    stack.append((u, 0))
            elif g[v] < 0:
                seen = set(g[u] for u in adj[v])
                x = 0
                while x in seen:
                    x += 1
                g[v] = x
    cnt = [None] * (n + 1)
    q = int(d[p]); p += 1
    out = []
    for _ in range(q):
        k = int(d[p]); p += 1
        pos = [int(x) for x in d[p:p + k]]; p += k
        X = 0
        for v in pos:
            X ^= g[v]
        total = 0
        if X:
            for v in pos:
                if cnt[v] is None:
                    cnt[v] = Counter(g[u] for u in adj[v])
                total += cnt[v].get(g[v] ^ X, 0)
        out.append(str(total))
    print('\n'.join(out))
main()
