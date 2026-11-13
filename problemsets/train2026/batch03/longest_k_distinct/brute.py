import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) <= k:
                best = max(best, j - i + 1)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
