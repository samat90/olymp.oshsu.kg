import sys

def sol(inp):
    s, t = inp.split()[:2]
    need = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    miss = len(t)
    have = {}
    l = 0
    best = -1
    for r, c in enumerate(s):
        if c in need:
            have[c] = have.get(c, 0) + 1
            if have[c] <= need[c]:
                miss -= 1
        while miss == 0:
            if best == -1 or r - l + 1 < best:
                best = r - l + 1
            d = s[l]
            if d in need:
                have[d] -= 1
                if have[d] < need[d]:
                    miss += 1
            l += 1
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
