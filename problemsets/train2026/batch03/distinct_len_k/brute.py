import sys

def brute(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    return str(len(set(s[i:i + k] for i in range(len(s) - k + 1))))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
