import sys

def sol(inp):
    a = inp.split()
    n = int(a[0])
    ws = a[1:n + 1]
    lo, hi = min(ws), max(ws)
    i = 0
    while i < len(lo) and lo[i] == hi[i]:
        i += 1
    return lo[:i] if i else '-'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
