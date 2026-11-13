import sys

def sol(inp):
    n = int(inp.split()[0])
    s = '1'
    for _ in range(n - 1):
        res = []
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            res.append(str(j - i) + s[i])
            i = j
        s = ''.join(res)
    return s


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
