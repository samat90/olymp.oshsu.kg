import sys

def sol(inp):
    s = inp.split()[0]
    last = [-1, -1, -1]
    ans = 0
    for i, c in enumerate(s):
        last[ord(c) - 97] = i
        ans += min(last) + 1
    return str(ans)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
