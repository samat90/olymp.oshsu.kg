import sys

def brute(inp):
    s, t = inp.split()[:2]
    best = -1
    for i in range(len(s)):
        for j in range(i, len(s)):
            w = s[i:j + 1]
            if all(w.count(c) >= t.count(c) for c in set(t)):
                if best == -1 or len(w) < best:
                    best = len(w)
                break
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
