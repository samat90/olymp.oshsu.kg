import sys

def brute(inp):
    s = inp.split()[0]
    return str(len(set(s[i:] + s[:i] for i in range(len(s)))))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
