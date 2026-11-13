import sys

def brute(inp):
    a, b = inp.split()[:2]
    from collections import deque
    al = sorted(set(a + b))
    lim = max(len(a), len(b)) + 1
    d = {a: 0}
    q = deque([a])
    while q:
        u = q.popleft()
        if u == b:
            return str(d[u])
        nb = []
        for i in range(len(u)):
            nb.append(u[:i] + u[i + 1:])
            for c in al:
                if c != u[i]:
                    nb.append(u[:i] + c + u[i + 1:])
        if len(u) < lim:
            for i in range(len(u) + 1):
                for c in al:
                    nb.append(u[:i] + c + u[i:])
        for v in nb:
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
