import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    res = []
    for i in range(n):
        j = 0
        while i + j < n and s[j] == s[i + j]:
            j += 1
        res.append(j)
    return ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
