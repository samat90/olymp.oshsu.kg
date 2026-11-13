import sys

def sol(inp):
    a = inp.split()
    s = a[0]
    m = int(a[1])
    from bisect import bisect_right
    pos = {}
    for i, c in enumerate(s):
        pos.setdefault(c, []).append(i)
    res = 0
    for w in a[2:2 + m]:
        p = -1
        ok = True
        for c in w:
            l = pos.get(c)
            if not l:
                ok = False
                break
            j = bisect_right(l, p)
            if j == len(l):
                ok = False
                break
            p = l[j]
        res += ok
    return str(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
