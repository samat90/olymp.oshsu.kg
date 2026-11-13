import sys

def sol(inp):
    from functools import cmp_to_key
    a = inp.split()
    n = int(a[0])
    w = a[1:n + 1]
    w.sort(key=cmp_to_key(lambda x, y: -1 if x + y > y + x else (1 if x + y < y + x else 0)))
    r = ''.join(w)
    return '0' if r[0] == '0' else r


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
