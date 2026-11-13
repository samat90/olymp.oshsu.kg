import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    best = 0
    for m in range(1, 1 << n):
        cnt = {}
        for i in range(n):
            if m >> i & 1:
                cnt[s[i]] = cnt.get(s[i], 0) + 1
        if sum(v % 2 for v in cnt.values()) <= 1:
            best = max(best, bin(m).count('1'))
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
