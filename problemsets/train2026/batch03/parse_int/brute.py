import sys

def brute(inp):
    import re
    lines = inp.split('\n')
    q = int(lines[0])
    out = []
    for line in lines[1:q + 1]:
        m = re.match(r' *([+-]?)([0-9]+)', line)
        if not m:
            out.append('0')
            continue
        v = int(m.group(2))
        if m.group(1) == '-':
            v = -v
        out.append(str(max(-2 ** 31, min(2 ** 31 - 1, v))))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
