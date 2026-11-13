import sys

def sol(inp):
    a, b = inp.split()[:2]
    i, j = len(a) - 1, len(b) - 1
    c = 0
    res = []
    while i >= 0 or j >= 0 or c:
        t = c
        if i >= 0:
            t += ord(a[i]) - 48
            i -= 1
        if j >= 0:
            t += ord(b[j]) - 48
            j -= 1
        res.append(chr(48 + t % 10))
        c = t // 10
    return ''.join(reversed(res))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
