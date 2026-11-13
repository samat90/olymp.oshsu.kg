import sys

def brute(inp):
    s = inp.split('\n')[0].rstrip('\r')
    t = ''.join(c for c in s if c.isalnum()).lower()
    i, j = 0, len(t) - 1
    while i < j:
        if t[i] != t[j]:
            return 'NO'
        i += 1
        j -= 1
    return 'YES'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
