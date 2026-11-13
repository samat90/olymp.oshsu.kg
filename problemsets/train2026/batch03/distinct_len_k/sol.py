import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    nxt = [{}]
    link = [-1]
    ln = [0]
    last = 0
    for c in s:
        cur = len(ln)
        ln.append(ln[last] + 1)
        link.append(0)
        nxt.append({})
        p = last
        while p != -1 and c not in nxt[p]:
            nxt[p][c] = cur
            p = link[p]
        if p != -1:
            q = nxt[p][c]
            if ln[p] + 1 == ln[q]:
                link[cur] = q
            else:
                cl = len(ln)
                ln.append(ln[p] + 1)
                nxt.append(dict(nxt[q]))
                link.append(link[q])
                while p != -1 and nxt[p].get(c) == q:
                    nxt[p][c] = cl
                    p = link[p]
                link[q] = link[cur] = cl
        last = cur
    return str(sum(1 for i in range(1, len(ln)) if ln[link[i]] < k <= ln[i]))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
