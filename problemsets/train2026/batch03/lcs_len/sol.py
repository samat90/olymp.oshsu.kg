import sys

def sol(inp):
    a, b = inp.split()[:2]
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return str(prev[-1])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
