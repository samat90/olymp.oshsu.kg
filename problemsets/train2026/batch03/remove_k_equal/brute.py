import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    ch = True
    while ch:
        ch = False
        for i in range(len(s) - k + 1):
            if s[i:i + k] == s[i] * k:
                s = s[:i] + s[i + k:]
                ch = True
                break
    return s or '-'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
