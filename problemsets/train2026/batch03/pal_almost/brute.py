import sys

def brute(inp):
    s = inp.split()[0]
    if s == s[::-1]:
        return 'YES'
    for i in range(len(s)):
        t = s[:i] + s[i + 1:]
        if t == t[::-1]:
            return 'YES'
    return 'NO'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
