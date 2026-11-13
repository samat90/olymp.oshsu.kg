import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    cuts = [0] + [i for i in range(1, n) if not (set(s[:i]) & set(s[i:]))] + [n]
    return ' '.join(str(cuts[i + 1] - cuts[i]) for i in range(len(cuts) - 1))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
