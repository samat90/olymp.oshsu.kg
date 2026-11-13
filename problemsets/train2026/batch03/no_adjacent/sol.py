import sys

def sol(inp):
    s = inp.split()[0]
    from collections import Counter
    return 'YES' if max(Counter(s).values()) <= (len(s) + 1) // 2 else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
