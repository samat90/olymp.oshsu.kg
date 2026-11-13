import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    return str(sum(1 for i in range(n) for j in range(i, n) if len(set(s[i:j + 1])) == 3))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
