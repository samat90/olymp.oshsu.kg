import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    return str(sum(1 for d in range(1, n) if n % d == 0 and s[:d] * (n // d) == s))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
