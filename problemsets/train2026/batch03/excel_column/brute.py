import sys

def brute(inp):
    a = inp.split()
    q = int(a[0])
    names = ['']
    cur = ['']
    for L in range(1, 4):
        nxt = []
        for p in cur:
            for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                nxt.append(p + c)
        names += nxt
        cur = nxt
    idx = {t: i for i, t in enumerate(names)}
    out = []
    for w in a[1:q + 1]:
        out.append(names[int(w)] if w.isdigit() else str(idx[w]))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
