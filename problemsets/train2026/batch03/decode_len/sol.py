import sys

def sol(inp):
    s = inp.split()[0]
    M = 10 ** 9 + 7
    st = [[0, 1]]
    num = 1
    for c in s:
        if c.isdigit():
            num = int(c)
        elif c == '[':
            st.append([0, num])
            num = 1
        elif c == ']':
            v, m = st.pop()
            st[-1][0] = (st[-1][0] + v * m) % M
        else:
            st[-1][0] = (st[-1][0] + 1) % M
    return str(st[0][0] % M)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
