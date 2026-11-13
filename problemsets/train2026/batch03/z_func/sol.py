import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    z = [0] * n
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return ' '.join(map(str, z))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
