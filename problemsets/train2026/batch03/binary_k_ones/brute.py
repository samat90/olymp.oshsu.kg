import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    n = len(s)
    return str(sum(1 for i in range(n) for j in range(i, n) if s[i:j + 1].count('1') == k))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
