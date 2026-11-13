import sys

def brute(inp):
    s = inp.split()[0]
    return ''.join(sorted(s, key=lambda ch: (-s.count(ch), ch)))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
