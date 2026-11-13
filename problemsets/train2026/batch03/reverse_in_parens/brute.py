import sys

def brute(inp):
    s = inp.split()[0]
    st = ['']
    for c in s:
        if c == '(':
            st.append('')
        elif c == ')':
            t = st.pop()
            st[-1] += t[::-1]
        else:
            st[-1] += c
    return st[0]


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
