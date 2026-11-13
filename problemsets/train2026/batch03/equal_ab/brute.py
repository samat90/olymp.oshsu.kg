import sys

def brute(inp):
    s = inp.split()[0]
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            t = s[i:j + 1]
            if t.count('a') == t.count('b'):
                best = max(best, len(t))
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
