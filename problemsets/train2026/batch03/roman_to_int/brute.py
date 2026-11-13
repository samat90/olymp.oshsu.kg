import sys

def brute(inp):
    a = inp.split()
    q = int(a[0])
    out = []
    for w in a[1:q + 1]:
        t = 0
        for tok, val in (('CM', 900), ('CD', 400), ('XC', 90), ('XL', 40), ('IX', 9), ('IV', 4)):
            while tok in w:
                w = w.replace(tok, '', 1)
                t += val
        for ch, val in (('M', 1000), ('D', 500), ('C', 100), ('L', 50), ('X', 10), ('V', 5), ('I', 1)):
            t += w.count(ch) * val
        out.append(str(t))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
