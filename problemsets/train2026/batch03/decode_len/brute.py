import sys

def brute(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7

    def parse(i):
        res = ''
        while i < len(s) and s[i] != ']':
            if s[i].isdigit():
                m = int(s[i])
                sub, i = parse(i + 2)
                res += sub * m
                i += 1
            else:
                res += s[i]
                i += 1
        return res, i
    return str(len(parse(0)[0]) % M)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
