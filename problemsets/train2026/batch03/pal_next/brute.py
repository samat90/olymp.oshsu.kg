import sys

def brute(inp):
    x = int(inp.split()[0]) + 1
    while True:
        t = str(x)
        if t == t[::-1]:
            return t
        x += 1


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
