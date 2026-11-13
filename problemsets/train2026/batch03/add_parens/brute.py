import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    best = 0
    for m in range(1 << n):
        b = 0
        ok = True
        for i in range(n):
            if m >> i & 1:
                b += 1 if s[i] == '(' else -1
                if b < 0:
                    ok = False
                    break
        if ok and b == 0:
            best = max(best, bin(m).count('1'))
    return str(n - best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
