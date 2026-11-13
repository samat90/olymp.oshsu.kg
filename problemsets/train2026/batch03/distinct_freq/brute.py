import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    best = 0
    for m in range(1 << n):
        cnt = {}
        for i in range(n):
            if m >> i & 1:
                cnt[s[i]] = cnt.get(s[i], 0) + 1
        v = list(cnt.values())
        if len(v) == len(set(v)):
            best = max(best, bin(m).count('1'))
    return str(n - best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
