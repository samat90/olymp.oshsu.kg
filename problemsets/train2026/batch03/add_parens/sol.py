import sys

def sol(inp):
    s = inp.split()[0]
    bal = 0
    add = 0
    for c in s:
        if c == '(':
            bal += 1
        elif bal:
            bal -= 1
        else:
            add += 1
    return str(add + bal)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
