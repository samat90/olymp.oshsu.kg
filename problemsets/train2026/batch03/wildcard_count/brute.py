import sys

def brute(inp):
    s, p = inp.split()[:2]
    n, m = len(s), len(p)
    return str(sum(1 for i in range(n - m + 1) if all(p[j] == '?' or p[j] == s[i + j] for j in range(m))))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
