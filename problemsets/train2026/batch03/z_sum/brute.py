import sys

def brute(inp):
    s = inp.split()[0]
    tot = 0
    for i in range(len(s)):
        j = 0
        while i + j < len(s) and s[j] == s[i + j]:
            j += 1
        tot += j
    return str(tot)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
