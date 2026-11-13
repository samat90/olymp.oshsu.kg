import sys

def sol(inp):
    s = inp.split()[0]
    res = []
    b = 0
    for c in s:
        if c == '(':
            if b:
                res.append(c)
            b += 1
        else:
            b -= 1
            if b:
                res.append(c)
    return ''.join(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
