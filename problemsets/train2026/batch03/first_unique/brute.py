import sys

def brute(inp):
    s = inp.split()[0]
    for i in range(len(s)):
        if s.count(s[i]) == 1:
            return str(i + 1)
    return '-1'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
