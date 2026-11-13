import sys

def sol(inp):
    s = inp.split()[0]
    n = len(s)
    match = [0] * n
    st = []
    for i, c in enumerate(s):
        if c == '(':
            st.append(i)
        elif c == ')':
            j = st.pop()
            match[i] = j
            match[j] = i
    res = []
    i = 0
    d = 1
    while 0 <= i < n:
        if s[i] in '()':
            i = match[i]
            d = -d
        else:
            res.append(s[i])
        i += d
    return ''.join(res)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
