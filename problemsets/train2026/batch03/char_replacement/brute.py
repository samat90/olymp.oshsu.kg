import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            t = s[i:j + 1]
            if len(t) - max(t.count(c) for c in set(t)) <= k:
                best = max(best, len(t))
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
