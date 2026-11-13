import sys

def brute(inp):
    a = inp.split()
    s = a[0]
    m = int(a[1])
    res = 0
    for w in a[2:2 + m]:
        for i in range(len(s) - len(w) + 1):
            if s[i:i + len(w)] == w:
                res += 1
    return str(res)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
