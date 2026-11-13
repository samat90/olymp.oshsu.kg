import sys

def sol(inp):
    s = inp.split()[0]
    from collections import Counter
    c = Counter(s)
    for i, ch in enumerate(s):
        if c[ch] == 1:
            return str(i + 1)
    return '-1'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
