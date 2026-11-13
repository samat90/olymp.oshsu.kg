import sys

def sol(inp):
    s = inp.split()[0]
    m = {')': '(', ']': '[', '}': '{'}
    st = []
    for c in s:
        if c in '([{':
            st.append(c)
        else:
            if not st or st.pop() != m[c]:
                return 'NO'
    return 'NO' if st else 'YES'


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
