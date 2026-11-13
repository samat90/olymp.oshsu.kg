import sys

def sol(inp):
    s = inp.split()[0]
    b = 0
    un = 0
    for c in s:
        if c == '[':
            b += 1
        elif b:
            b -= 1
        else:
            un += 1
    return str((un + 1) // 2)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
