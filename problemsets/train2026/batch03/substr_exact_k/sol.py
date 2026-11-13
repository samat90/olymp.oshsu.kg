import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]

    def most(m):
        if m == 0:
            return 0
        cnt = {}
        l = 0
        res = 0
        for r, c in enumerate(s):
            cnt[c] = cnt.get(c, 0) + 1
            while len(cnt) > m:
                d = s[l]
                cnt[d] -= 1
                if cnt[d] == 0:
                    del cnt[d]
                l += 1
            res += r - l + 1
        return res
    return str(most(k) - most(k - 1))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
