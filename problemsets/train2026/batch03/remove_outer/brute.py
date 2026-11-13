import sys

def brute(inp):
    s = inp.split()[0]
    parts = []
    b = 0
    st = 0
    for i, c in enumerate(s):
        b += 1 if c == '(' else -1
        if b == 0:
            parts.append(s[st + 1:i])
            st = i + 1
    return ''.join(parts)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
