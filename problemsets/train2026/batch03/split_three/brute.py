import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    cnt = 0
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            x, y, z = s[:i].count('1'), s[i:j].count('1'), s[j:].count('1')
            if x == y == z:
                cnt += 1
    return str(cnt % (10 ** 9 + 7))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
