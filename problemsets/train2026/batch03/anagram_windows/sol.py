import sys

def sol(inp):
    s, p = inp.split()[:2]
    m = len(p)
    cnt = [0] * 26
    for c in p:
        cnt[ord(c) - 97] += 1
    for c in s[:m]:
        cnt[ord(c) - 97] -= 1
    bad = sum(1 for x in cnt if x)
    ans = 1 if bad == 0 else 0
    for i in range(m, len(s)):
        for c, d in ((s[i], -1), (s[i - m], 1)):
            j = ord(c) - 97
            if cnt[j]:
                bad -= 1
            cnt[j] += d
            if cnt[j]:
                bad += 1
        if bad == 0:
            ans += 1
    return str(ans)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
