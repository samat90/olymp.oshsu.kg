import sys

def brute(inp):
    s = inp.split()[0]
    pos = [i for i, c in enumerate(s) if c == '?']
    cnt = 0
    for m in range(1 << len(pos)):
        t = list(s)
        for j, p in enumerate(pos):
            t[p] = '(' if m >> j & 1 else ')'
        b = 0
        ok = True
        for c in t:
            b += 1 if c == '(' else -1
            if b < 0:
                ok = False
                break
        if ok and b == 0:
            cnt += 1
    return str(cnt % (10 ** 9 + 7))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
