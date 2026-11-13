import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    return str(min(s[:i].count('1') + s[i:].count('0') for i in range(n + 1)))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
