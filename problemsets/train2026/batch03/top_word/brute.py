import sys

def brute(inp):
    a = inp.split()
    n = int(a[0])
    ws = a[1:n + 1]
    best = None
    for w in sorted(set(ws)):
        cnt = ws.count(w)
        if best is None or cnt > best[1]:
            best = (w, cnt)
    return '%s %d' % best


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
