import sys

def sol(inp):
    s = inp.split()[0]
    from collections import Counter
    cs = sorted(Counter(s).values(), reverse=True)
    used = set()
    ans = 0
    for c in cs:
        while c > 0 and c in used:
            c -= 1
            ans += 1
        if c > 0:
            used.add(c)
    return str(ans)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
