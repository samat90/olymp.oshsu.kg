import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    cnt = 0
    for i in range(n):
        for j in range(i + 2, n + 1, 2):
            t = s[i:j]
            h = len(t) // 2
            if t == '0' * h + '1' * h or t == '1' * h + '0' * h:
                cnt += 1
    return str(cnt)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
