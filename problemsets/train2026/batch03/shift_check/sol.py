import sys

def sol(inp):
    s, t = inp.split()[:2]
    n = len(s)
    w = t + '#' + s + s
    pi = [0] * len(w)
    for i in range(1, len(w)):
        j = pi[i - 1]
        while j and w[i] != w[j]:
            j = pi[j - 1]
        if w[i] == w[j]:
            j += 1
        pi[i] = j
        if j == n:
            st = i - 2 * n
            if st < n:
                return str(st)
    return '-1'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
