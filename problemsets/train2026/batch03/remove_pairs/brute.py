import sys

def brute(inp):
    s = inp.split()[0]
    ch = True
    while ch:
        ch = False
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                s = s[:i] + s[i + 2:]
                ch = True
                break
    return s or '-'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
