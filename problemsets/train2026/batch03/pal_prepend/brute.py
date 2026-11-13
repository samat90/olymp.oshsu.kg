import sys

def brute(inp):
    s = inp.split()[0]
    r = s[::-1]
    for t in range(len(s) + 1):
        c = r[:t] + s
        if c == c[::-1]:
            return c


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
