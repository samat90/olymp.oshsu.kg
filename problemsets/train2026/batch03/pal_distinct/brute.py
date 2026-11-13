import sys

def brute(inp):
    s = inp.split()[0]
    n = len(s)
    st = set()
    for i in range(n):
        for j in range(i, n):
            t = s[i:j + 1]
            if t == t[::-1]:
                st.add(t)
    return str(len(st))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
