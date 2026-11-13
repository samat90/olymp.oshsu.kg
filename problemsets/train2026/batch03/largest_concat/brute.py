import sys

def brute(inp):
    from itertools import permutations
    a = inp.split()
    n = int(a[0])
    w = a[1:n + 1]
    best = max(permutations(w), key=lambda p: (len(''.join(p).lstrip('0')), ''.join(p)))
    r = ''.join(best)
    return '0' if r[0] == '0' else r


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
