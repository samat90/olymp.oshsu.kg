import sys

def sol(inp):
    s = inp.split()[0]
    last = {c: i for i, c in enumerate(s)}
    res = []
    st = end = 0
    for i, c in enumerate(s):
        end = max(end, last[c])
        if i == end:
            res.append(i - st + 1)
            st = i + 1
    return ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
