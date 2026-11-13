import sys

def sol(inp):
    a, b = inp.split()[:2]
    from collections import Counter
    return 'YES' if Counter(a) == Counter(b) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
