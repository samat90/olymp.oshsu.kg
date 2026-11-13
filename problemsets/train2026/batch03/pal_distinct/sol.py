import sys

def sol(inp):
    s = inp.split()[0]
    ln = [-1, 0]
    link = [0, 0]
    nxt = [{}, {}]
    last = 1
    for i, c in enumerate(s):
        cur = last
        while True:
            l = ln[cur]
            if i - l - 1 >= 0 and s[i - l - 1] == c:
                break
            cur = link[cur]
        if c in nxt[cur]:
            last = nxt[cur][c]
            continue
        ln.append(ln[cur] + 2)
        nxt.append({})
        new = len(ln) - 1
        if ln[new] == 1:
            link.append(1)
        else:
            p = link[cur]
            while True:
                l = ln[p]
                if i - l - 1 >= 0 and s[i - l - 1] == c:
                    break
                p = link[p]
            link.append(nxt[p][c])
        nxt[cur][c] = new
        last = new
    return str(len(ln) - 2)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
