import sys

def brute(inp):
    a = inp.split()
    n = int(a[0])
    ws = a[1:n + 1]
    groups = []
    for w in ws:
        for g in groups:
            if sorted(g) == sorted(w):
                break
        else:
            groups.append(w)
    return str(len(groups))


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
