import sys

def brute(inp):
    s = inp.split()[0]
    while '//' in s:
        s = s.replace('//', '/')
    parts = s.strip('/').split('/') if s.strip('/') else []
    res = []
    i = 0
    while i < len(parts):
        if parts[i] == '.':
            pass
        elif parts[i] == '..':
            if res:
                res = res[:-1]
        else:
            res = res + [parts[i]]
        i += 1
    return '/' + '/'.join(res)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
