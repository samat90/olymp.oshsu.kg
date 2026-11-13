import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    pi = [0] * n
    for i in range(1, n):
        j = pi[i - 1]
        while j and s[i] != s[j]:
            j = pi[j - 1]
        if s[i] == s[j]:
            j += 1
        pi[i] = j
    p = n - pi[-1]
    return str(p if n % p == 0 else n)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
