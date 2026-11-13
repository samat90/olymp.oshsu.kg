import sys

def brute(inp):
    s, p = inp.split()[:2]
    res = [i + 1 for i in range(len(s) - len(p) + 1) if s[i:i + len(p)] == p]
    if not res:
        return '0'
    return str(len(res)) + '\n' + ' '.join(map(str, res))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
