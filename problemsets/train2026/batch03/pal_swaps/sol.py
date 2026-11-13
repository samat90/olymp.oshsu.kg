import sys

def sol(inp):
    s = list(inp.split()[0])
    n = len(s)
    ans = 0
    l, r = 0, n - 1
    while l < r:
        k = r
        while k > l and s[k] != s[l]:
            k -= 1
        if k == l:
            s[l], s[l + 1] = s[l + 1], s[l]
            ans += 1
            continue
        for j in range(k, r):
            s[j], s[j + 1] = s[j + 1], s[j]
            ans += 1
        l += 1
        r -= 1
    return str(ans)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
