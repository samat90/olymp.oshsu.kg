import sys

def brute(inp):
    a = inp.split()
    n = int(a[0])
    ws = a[1:n + 1]
    p = ws[0]
    for w in ws[1:]:
        while not w.startswith(p):
            p = p[:-1]
    return p if p else '-'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
