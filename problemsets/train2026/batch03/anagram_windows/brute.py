import sys

def brute(inp):
    s, p = inp.split()[:2]
    m = len(p)
    sp = sorted(p)
    return str(sum(1 for i in range(len(s) - m + 1) if sorted(s[i:i + m]) == sp))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
