import sys

def sol(inp):
    s = inp.split()[0]
    st = []
    for c in s:
        if st and st[-1] == c:
            st.pop()
        else:
            st.append(c)
    return ''.join(st) or '-'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
