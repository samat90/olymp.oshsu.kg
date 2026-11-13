import sys

def sol(inp):
    s, p = inp.split()[:2]
    t = p + '#' + s
    pi = [0] * len(t)
    res = []
    m = len(p)
    for i in range(1, len(t)):
        j = pi[i - 1]
        while j and t[i] != t[j]:
            j = pi[j - 1]
        if t[i] == t[j]:
            j += 1
        pi[i] = j
        if j == m:
            res.append(i - 2 * m + 1)
    if not res:
        return '0'
    return str(len(res)) + '\n' + ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
