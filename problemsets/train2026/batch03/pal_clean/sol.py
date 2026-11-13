import sys

def sol(inp):
    s = inp.split('\n')[0].rstrip('\r')
    t = [c.lower() for c in s if c.isalnum()]
    return 'YES' if t == t[::-1] else 'NO'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
