import sys

def brute(inp):
    o, s = inp.split()[:2]
    return ''.join(sorted(s, key=lambda c: (o.index(c) if c in o else 100, c)))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
