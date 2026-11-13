import sys

def sol(inp):
    o, s = inp.split()[:2]
    pos = {c: i for i, c in enumerate(o)}
    cnt = {}
    for c in s:
        cnt[c] = cnt.get(c, 0) + 1
    res = [c * cnt[c] for c in o if c in cnt]
    rest = sorted(c for c in cnt if c not in pos)
    res += [c * cnt[c] for c in rest]
    return ''.join(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
