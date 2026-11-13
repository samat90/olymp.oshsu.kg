import sys

def brute(inp):
    s = inp.split()[0]
    return str(len(set(s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1))))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
