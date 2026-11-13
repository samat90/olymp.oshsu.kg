import sys

def sol(inp):
    a = inp.split()
    n = int(a[0])
    ws = sorted(set(a[1:n + 1]), key=lambda w: (len(w), w))
    ok = set()
    best = '-'
    for w in ws:
        if len(w) == 1 or w[:-1] in ok:
            ok.add(w)
            if best == '-' or len(w) > len(best):
                best = w
    return best


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
