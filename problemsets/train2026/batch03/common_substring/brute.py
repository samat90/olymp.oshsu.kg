import sys

def brute(inp):
    a, b = inp.split()[:2]
    best = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            if a[i:j] in b:
                best = max(best, j - i)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
