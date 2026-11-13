import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    for L in range(n - 1, 0, -1):
        seen = set()
        for i in range(n - L + 1):
            t = s[i:i + L]
            if t in seen:
                return str(L)
            seen.add(t)
    return '0'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
