import sys

def sol(inp):
    s = inp.split()[0]
    st = []
    for p in s.split('/'):
        if p == '' or p == '.':
            continue
        if p == '..':
            if st:
                st.pop()
        else:
            st.append(p)
    return '/' + '/'.join(st)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
