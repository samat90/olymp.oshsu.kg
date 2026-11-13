import sys

def brute(inp):
    a, b = inp.split()[:2]
    return bin(int(a, 2) + int(b, 2))[2:]


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
