import sys

def brute(inp):
    a = inp.split()
    n = int(a[0])
    st = set(a[1:n + 1])
    best = '-'
    for w in sorted(st):
        if all(w[:i] in st for i in range(1, len(w) + 1)):
            if best == '-' or len(w) > len(best):
                best = w
    return best


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
