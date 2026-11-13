import sys

def sol(inp):
    s = inp.split()[0]
    runs = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        runs.append(j - i)
        i = j
    return str(sum(min(runs[i], runs[i + 1]) for i in range(len(runs) - 1)))


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
