import sys

def sol(inp):
    s = inp.split()[0]
    from collections import Counter
    c = Counter(s)
    return ''.join(ch * c[ch] for ch in sorted(c, key=lambda x: (-c[x], x)))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
