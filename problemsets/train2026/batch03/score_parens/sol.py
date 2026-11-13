import sys

def sol(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7
    st = [0]
    for c in s:
        if c == '(':
            st.append(0)
        else:
            v = st.pop()
            st[-1] = (st[-1] + (1 if v == 0 else 2 * v)) % M
    return str(st[0] % M)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
