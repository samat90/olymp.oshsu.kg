import sys

def brute(inp):
    a = inp.split()
    p = a[0]
    ws = a[1:]
    for i in range(len(p)):
        for j in range(len(p)):
            if (p[i] == p[j]) != (ws[i] == ws[j]):
                return 'NO'
    return 'YES'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
