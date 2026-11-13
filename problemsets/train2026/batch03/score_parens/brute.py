import sys

def brute(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7

    def f(l, r):
        if l >= r:
            return 0
        b = 0
        for i in range(l, r):
            b += 1 if s[i] == '(' else -1
            if b == 0:
                inner = f(l + 1, i)
                return ((1 if inner == 0 else 2 * inner) + f(i + 1, r)) % M
    return str(f(0, len(s)) % M)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
