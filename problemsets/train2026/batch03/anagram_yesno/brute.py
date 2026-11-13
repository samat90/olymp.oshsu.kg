import sys

def brute(inp):
    a, b = inp.split()[:2]
    return 'YES' if sorted(a) == sorted(b) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
