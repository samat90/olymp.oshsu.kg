import sys

def brute(inp):
    s, p = inp.split()[:2]
    m = len(p)
    pos = [i for i in range(len(s) - m + 1) if s[i:i + m] == p]
    non = 0
    nxt = 0
    for i in pos:
        if i >= nxt:
            non += 1
            nxt = i + m
    return '%d %d' % (len(pos), non)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
