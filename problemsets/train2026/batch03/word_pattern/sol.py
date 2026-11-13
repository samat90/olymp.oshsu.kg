import sys

def sol(inp):
    a = inp.split()
    p = a[0]
    ws = a[1:]
    if len(ws) != len(p):
        return 'NO'
    d1, d2 = {}, {}
    for c, w in zip(p, ws):
        if d1.setdefault(c, w) != w or d2.setdefault(w, c) != c:
            return 'NO'
    return 'YES'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
