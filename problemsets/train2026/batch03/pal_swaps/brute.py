import sys

def brute(inp):
    s = inp.split()[0]
    from collections import deque
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        if u == u[::-1]:
            return str(d[u])
        for i in range(len(u) - 1):
            v = u[:i] + u[i + 1] + u[i] + u[i + 2:]
            if v not in d:
                d[v] = d[u] + 1
                q.append(v)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
