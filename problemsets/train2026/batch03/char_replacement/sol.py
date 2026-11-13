import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    cnt = [0] * 26
    l = 0
    mx = 0
    best = 0
    for r, c in enumerate(s):
        j = ord(c) - 65
        cnt[j] += 1
        mx = max(mx, cnt[j])
        if r - l + 1 - mx > k:
            cnt[ord(s[l]) - 65] -= 1
            l += 1
        best = max(best, r - l + 1)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
