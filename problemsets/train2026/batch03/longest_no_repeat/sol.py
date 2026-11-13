import sys

def sol(inp):
    s = inp.split()[0]
    last = {}
    st = 0
    best = 0
    for i, c in enumerate(s):
        if c in last and last[c] >= st:
            st = last[c] + 1
        last[c] = i
        if i - st + 1 > best:
            best = i - st + 1
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
