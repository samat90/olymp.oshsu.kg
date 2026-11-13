import sys

def sol(inp):
    a, b = inp.split()[:2]
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return str(prev[-1])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
