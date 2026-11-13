import sys

def sol(inp):
    a = inp.split()
    q = int(a[0])
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    out = []
    for w in a[1:q + 1]:
        t = 0
        for i, c in enumerate(w):
            if i + 1 < len(w) and v[c] < v[w[i + 1]]:
                t -= v[c]
            else:
                t += v[c]
        out.append(str(t))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
