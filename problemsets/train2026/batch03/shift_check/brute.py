import sys

def brute(inp):
    s, t = inp.split()[:2]
    for k in range(len(s)):
        if s[k:] + s[:k] == t:
            return str(k)
    return '-1'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
