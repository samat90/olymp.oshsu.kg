import sys

def brute(inp):
    s = inp.split()[0]
    from collections import deque

    def ok(t):
        b = 0
        for c in t:
            b += 1 if c == '[' else -1
            if b < 0:
                return False
        return b == 0
    d = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        if ok(u):
            return str(d[u])
        for i in range(len(u)):
            for j in range(i + 1, len(u)):
                if u[i] != u[j]:
                    v = list(u)
                    v[i], v[j] = v[j], v[i]
                    v = ''.join(v)
                    if v not in d:
                        d[v] = d[u] + 1
                        q.append(v)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
