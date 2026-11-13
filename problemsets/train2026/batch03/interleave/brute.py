import sys

def brute(inp):
    a, b, c = inp.split()[:3]
    if len(a) + len(b) != len(c):
        return 'NO'

    def go(i, j):
        if i + j == len(c):
            return True
        if i < len(a) and a[i] == c[i + j] and go(i + 1, j):
            return True
        if j < len(b) and b[j] == c[i + j] and go(i, j + 1):
            return True
        return False
    return 'YES' if go(0, 0) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
