import sys

def sol(inp):
    a = inp.split()
    k = int(a[0])
    s = a[1]
    st = []
    for c in s:
        while k and st and st[-1] > c:
            st.pop()
            k -= 1
        st.append(c)
    if k:
        st = st[:-k]
    return ''.join(st).lstrip('0') or '0'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
