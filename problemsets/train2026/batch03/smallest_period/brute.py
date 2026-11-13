import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    for p in range(1, n + 1):
        if all(s[i] == s[i + p] for i in range(n - p)):
            return str(p)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
