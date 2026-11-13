import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    st = []
    for c in s:
        if st and st[-1][0] == c:
            st[-1][1] += 1
            if st[-1][1] == k:
                st.pop()
        else:
            st.append([c, 1])
    return ''.join(c * m for c, m in st) or '-'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
