import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    best = [0] * 26
    for c in s:
        j = ord(c) - 97
        v = max(best[max(0, j - k):min(26, j + k + 1)]) + 1
        if v > best[j]:
            best[j] = v
    return str(max(best))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
