import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    v = 'aeiou'
    cur = sum(1 for c in s[:k] if c in v)
    best = cur
    for i in range(k, len(s)):
        cur += (s[i] in v) - (s[i - k] in v)
        best = max(best, cur)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
