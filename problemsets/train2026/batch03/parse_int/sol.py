import sys

def sol(inp):
    lines = inp.split('\n')
    q = int(lines[0])
    out = []
    for line in lines[1:q + 1]:
        i = 0
        n = len(line)
        while i < n and line[i] == ' ':
            i += 1
        sg = 1
        if i < n and line[i] in '+-':
            if line[i] == '-':
                sg = -1
            i += 1
        v = 0
        while i < n and '0' <= line[i] <= '9':
            v = v * 10 + ord(line[i]) - 48
            if v > 2 ** 31:
                v = 2 ** 31
            i += 1
        v *= sg
        v = max(-2 ** 31, min(2 ** 31 - 1, v))
        out.append(str(v))
    return '\n'.join(out)


if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()) + "\n")
