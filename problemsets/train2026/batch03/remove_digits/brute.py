import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    n = len(s)
    from itertools import combinations
    best = None
    for idx in combinations(range(n), n - k):
        t = ''.join(s[i] for i in idx).lstrip('0') or '0'
        key = (len(t), t)
        if best is None or key < best:
            best = key
    return best[1]


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
