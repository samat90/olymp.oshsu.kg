import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def sol(s):
    n,m=map(int,s.split())
    ms=[x for x in range(1<<m) if not x&(x>>1)]
    nb={a:[b for b in ms if not a&b] for a in ms}
    dp={a:1 for a in ms}
    for _ in range(n-1):
        dp={b:sum(dp[a] for a in nb[b])%M for b in ms}
    return sum(dp.values())%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
