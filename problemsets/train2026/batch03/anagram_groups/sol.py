import sys

def sol(inp):
    a = inp.split()
    n = int(a[0])
    return str(len(set(''.join(sorted(w)) for w in a[1:n + 1])))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
