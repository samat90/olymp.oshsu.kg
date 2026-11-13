import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    cnt = {}
    l = 0
    best = 0
    for r, c in enumerate(s):
        cnt[c] = cnt.get(c, 0) + 1
        while len(cnt) > k:
            d = s[l]
            cnt[d] -= 1
            if cnt[d] == 0:
                del cnt[d]
            l += 1
        best = max(best, r - l + 1)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
