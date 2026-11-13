import sys

def brute(inp):
    a, b = inp.split()[:2]
    pool = list(b)
    for c in a:
        if c in pool:
            pool.remove(c)
        else:
            return 'NO'
    return 'YES'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
