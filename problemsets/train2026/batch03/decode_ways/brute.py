import sys

def brute(inp):
    s = inp.split()[0]

    def go(i):
        if i == len(s):
            return 1
        if s[i] == '0':
            return 0
        r = go(i + 1)
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26:
            r += go(i + 2)
        return r
    return str(go(0) % (10 ** 9 + 7))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
