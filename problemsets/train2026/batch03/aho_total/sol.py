import sys

def sol(inp):
    a = inp.split()
    s = a[0]
    m = int(a[1])
    go = [{}]
    cnt = [0]
    for w in a[2:2 + m]:
        v = 0
        for c in w:
            if c not in go[v]:
                go.append({})
                cnt.append(0)
                go[v][c] = len(go) - 1
            v = go[v][c]
        cnt[v] += 1
    fail = [0] * len(go)
    order = []
    q = list(go[0].values())
    order = q[:]
    i = 0
    while i < len(q):
        u = q[i]
        i += 1
        for c, v in go[u].items():
            f = fail[u]
            while f and c not in go[f]:
                f = fail[f]
            fail[v] = go[f][c] if c in go[f] and go[f][c] != v else 0
            q.append(v)
    for u in q:
        cnt[u] += cnt[fail[u]]
    v = 0
    res = 0
    for c in s:
        while v and c not in go[v]:
            v = fail[v]
        v = go[v].get(c, 0)
        res += cnt[v]
    return str(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
