import sys

def brute(inp):
    from itertools import groupby
    n = int(inp.split()[0])
    s = '1'
    for _ in range(n - 1):
        s = ''.join(str(len(list(g))) + k for k, g in groupby(s))
    return s


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
