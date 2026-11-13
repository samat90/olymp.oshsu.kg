import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    d = s + s
    i, j, k = 0, 1, 0
    while i < n and j < n and k < n:
        a, b = d[i + k], d[j + k]
        if a == b:
            k += 1
            continue
        if a > b:
            i += k + 1
        else:
            j += k + 1
        if i == j:
            j += 1
        k = 0
    st = min(i, j)
    return d[st:st + n]


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
