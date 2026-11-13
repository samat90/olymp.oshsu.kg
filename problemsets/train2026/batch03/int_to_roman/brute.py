import sys

def brute(inp):
    a = inp.split()
    q = int(a[0])
    th = ['', 'M', 'MM', 'MMM']
    h = ['', 'C', 'CC', 'CCC', 'CD', 'D', 'DC', 'DCC', 'DCCC', 'CM']
    te = ['', 'X', 'XX', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC']
    o = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
    out = []
    for x in a[1:q + 1]:
        x = int(x)
        out.append(th[x // 1000] + h[x // 100 % 10] + te[x // 10 % 10] + o[x % 10])
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
