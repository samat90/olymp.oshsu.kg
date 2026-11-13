import sys

def brute(inp):
    s, p = inp.split()[:2]
    import re
    rx = ''.join('.*' if c == '*' else '.' if c == '?' else c for c in p)
    return 'YES' if re.fullmatch(rx, s) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
