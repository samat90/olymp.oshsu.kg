import sys

def brute(inp):
    s = inp.split()[0]
    st = set()
    for m in range(1, 1 << len(s)):
        st.add(''.join(s[i] for i in range(len(s)) if m >> i & 1))
    return str(len(st) % (10 ** 9 + 7))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
