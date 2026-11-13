import sys

def sol(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7
    end = [0] * 26
    tot = 1
    for c in s:
        j = ord(c) - 97
        nt = (2 * tot - end[j]) % M
        end[j] = tot
        tot = nt
    return str((tot - 1) % M)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
