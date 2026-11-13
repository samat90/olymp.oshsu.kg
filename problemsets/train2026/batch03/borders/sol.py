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
    res = []
    j = pi[-1]
    while j:
        res.append(j)
        j = pi[j - 1]
    res.reverse()
    if not res:
        return '0'
    return str(len(res)) + '\n' + ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
