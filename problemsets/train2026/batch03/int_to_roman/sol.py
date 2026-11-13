import sys

def sol(inp):
    a = inp.split()
    q = int(a[0])
    t = [(1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
         (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')]
    out = []
    for x in a[1:q + 1]:
        x = int(x)
        r = []
        for v, s in t:
            while x >= v:
                r.append(s)
                x -= v
        out.append(''.join(r))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
