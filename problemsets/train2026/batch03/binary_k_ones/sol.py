import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    cnt = {0: 1}
    pre = 0
    ans = 0
    for c in s:
        if c == '1':
            pre += 1
        ans += cnt.get(pre - k, 0)
        cnt[pre] = cnt.get(pre, 0) + 1
    return str(ans)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
