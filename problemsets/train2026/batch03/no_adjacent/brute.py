import sys

def brute(inp):
    s = inp.split()[0]
    from collections import Counter
    c = Counter(s)
    n = len(s)

    def go(prev, left):
        if left == 0:
            return True
        for ch in list(c):
            if ch != prev and c[ch] > 0:
                c[ch] -= 1
                ok = go(ch, left - 1)
                c[ch] += 1
                if ok:
                    return True
        return False
    return 'YES' if go('', n) else 'NO'


if __name__ == "__main__":
    sys.stdout.write(brute(sys.stdin.read()) + "\n")
