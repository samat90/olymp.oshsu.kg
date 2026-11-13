import sys

def sol(inp):
    s, p = inp.split()[:2]
    m = len(p)
    t = p + '#' + s
    pi = [0] * len(t)
    tot = 0
    non = 0
    last = -1
    for i in range(1, len(t)):
        j = pi[i - 1]
        while j and t[i] != t[j]:
            j = pi[j - 1]
        if t[i] == t[j]:
            j += 1
        pi[i] = j
        if j == m:
            tot += 1
            st = i - 2 * m
            if st > last:
                non += 1
                last = st + m - 1
    return '%d %d' % (tot, non)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
