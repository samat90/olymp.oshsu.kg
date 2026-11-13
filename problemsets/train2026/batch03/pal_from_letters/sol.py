import sys

def sol(inp):
    s = inp.split()[0]
    from collections import Counter
    c = Counter(s)
    ans = sum(v // 2 * 2 for v in c.values())
    if any(v % 2 for v in c.values()):
        ans += 1
    return str(ans)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
