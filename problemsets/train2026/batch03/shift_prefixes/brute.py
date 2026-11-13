import sys

def brute(inp):
    a = inp.split()
    s = list(a[0])
    n = len(s)
    x = [int(t) for t in a[1:n + 1]]
    for i in range(n):
        for j in range(i + 1):
            s[j] = chr((ord(s[j]) - 97 + x[i]) % 26 + 97)
    return ''.join(s)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
