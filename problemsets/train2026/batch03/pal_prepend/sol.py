import sys

def sol(inp):
    s = inp.split()[0]
    r = s[::-1]
    t = s + '#' + r
    pi = [0] * len(t)
    for i in range(1, len(t)):
        j = pi[i - 1]
        while j and t[i] != t[j]:
            j = pi[j - 1]
        if t[i] == t[j]:
            j += 1
        pi[i] = j
    L = pi[-1]
    return s[L:][::-1] + s


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
