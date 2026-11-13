import sys

def sol(inp):
    s = inp.split()[0]
    ones = s.count('1')
    zeros = 0
    best = -1
    for i in range(len(s) - 1):
        if s[i] == '0':
            zeros += 1
        else:
            ones -= 1
        best = max(best, zeros + ones)
    return str(best)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
