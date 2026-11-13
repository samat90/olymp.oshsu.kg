import sys

def brute(inp):
    a = inp.split()
    s = a[0]
    m = int(a[1])
    ws = a[2:2 + m]

    def go(i):
        if i == len(s):
            return 1
        return sum(go(i + len(w)) for w in ws if s.startswith(w, i))
    return str(go(0) % (10 ** 9 + 7))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
