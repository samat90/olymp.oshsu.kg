import sys

def sol(inp):
    a = inp.split()
    q = int(a[0])
    out = []
    for w in a[1:q + 1]:
        if w.isdigit():
            x = int(w)
            t = ''
            while x:
                x -= 1
                t = chr(65 + x % 26) + t
                x //= 26
            out.append(t)
        else:
            v = 0
            for c in w:
                v = v * 26 + ord(c) - 64
            out.append(str(v))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
