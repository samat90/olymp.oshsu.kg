import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    d = s + s
    diff = 0
    best = n
    for i in range(2 * n):
        if (ord(d[i]) - 48) != i % 2:
            diff += 1
        if i >= n and (ord(d[i - n]) - 48) != (i - n) % 2:
            diff -= 1
        if i >= n - 1:
            best = min(best, diff, n - diff)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
