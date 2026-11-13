import sys, random, heapq, bisect, re, math
from collections import deque, Counter, defaultdict
MOD = 10**9 + 7
def sc(k, hi):
    return max(3, int(hi ** (k / 10)))

def sol(s):
    s = s.split()[0]
    nums = []; ops = []
    prec = {'+': 1, '-': 1, '*': 2}
    def ap():
        o = ops.pop(); b = nums.pop(); a = nums.pop()
        nums.append((a + b) % MOD if o == '+' else (a - b) % MOD if o == '-' else a * b % MOD)
    i = 0; n = len(s)
    while i < n:
        c = s[i]
        if c.isdigit():
            j = i
            while j < n and s[j].isdigit(): j += 1
            nums.append(int(s[i:j]) % MOD); i = j; continue
        if c == '(': ops.append(c)
        elif c == ')':
            while ops[-1] != '(': ap()
            ops.pop()
        else:
            while ops and ops[-1] != '(' and prec[ops[-1]] >= prec[c]: ap()
            ops.append(c)
        i += 1
    while ops: ap()
    return str(nums[0] % MOD)

if __name__ == "__main__":
    sys.stdout.write(sol(sys.stdin.read()).strip() + "\n")
