import sys

def brute(inp):
    from itertools import groupby
    s = inp.split()[0]
    return ''.join(k + str(len(list(g))) for k, g in groupby(s))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
