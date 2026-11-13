import sys

def sol(inp):
    s = inp.split()[0]
    pi = [0] * len(s)
    for i in range(1, len(s)):
        j = pi[i - 1]
        while j and s[i] != s[j]:
            j = pi[j - 1]
        if s[i] == s[j]:
            j += 1
        pi[i] = j
    return str(len(s) - pi[-1])


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
