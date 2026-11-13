import sys

def brute(inp):
    s, t = inp.split()[:2]
    n = len(s)
    cnt = 0
    for m in range(1 << n):
        if bin(m).count('1') == len(t) and ''.join(s[i] for i in range(n) if m >> i & 1) == t:
            cnt += 1
    return str(cnt % (10 ** 9 + 7))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
