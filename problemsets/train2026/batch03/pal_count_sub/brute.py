import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    cnt = 0
    for i in range(n):
        for j in range(i, n):
            t = s[i:j + 1]
            if t == t[::-1]:
                cnt += 1
    return str(cnt)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
