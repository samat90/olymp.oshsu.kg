import sys

def brute(inp):
    s = inp.split()[0]
    while True:
        t = s.replace('()', '').replace('[]', '').replace('{}', '')
        if t == s:
            break
        s = t
    return 'YES' if not s else 'NO'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
