import sys

d = sys.stdin.read().split()
n, m, q = int(d[0]), int(d[1]), int(d[2])
E = [(int(d[3 + 2 * i]), int(d[4 + 2 * i])) for i in range(m)]
pos = 3 + 2 * m


def connected(skip, u, v):
    adj = [[] for _ in range(n + 1)]
    for i, (a, b) in enumerate(E):
        if i != skip:
            adj[a].append(b)
            adj[b].append(a)
    seen = {u}
    st = [u]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                st.append(y)
    return v in seen


out = []
for _ in range(q):
    u, v = int(d[pos]), int(d[pos + 1])
    pos += 2
    out.append(sum(1 for i in range(m) if not connected(i, u, v)))
print('\n'.join(map(str, out)))
