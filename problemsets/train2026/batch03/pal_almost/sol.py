import sys

def sol(inp):
    s = inp.split()[0]

    def pal(i, j):
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return 'YES' if pal(i + 1, j) or pal(i, j - 1) else 'NO'
        i += 1
        j -= 1
    return 'YES'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
