import sys

def brute(inp):
    s = inp.split()[0]
    return str(max(s[:i].count('0') + s[i:].count('1') for i in range(1, len(s))))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
