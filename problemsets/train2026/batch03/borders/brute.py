import sys

def brute(inp):
    s = inp.split()[0]
    res = [l for l in range(1, len(s)) if s[:l] == s[len(s) - l:]]
    if not res:
        return '0'
    return str(len(res)) + '\n' + ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
