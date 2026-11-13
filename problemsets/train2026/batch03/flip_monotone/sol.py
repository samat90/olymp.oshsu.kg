import sys

def sol(inp):
    s = inp.split()[0]
    ones = 0
    res = 0
    for c in s:
        if c == '1':
            ones += 1
        else:
            res = min(res + 1, ones)
    return str(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
