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
    import math
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]
    sq=lambda x: math.isqrt(x)**2==x
    ok=[[sq(a[i]+a[j]) for j in range(n)] for i in range(n)]
    F=1<<n; dp=[[0]*n for _ in range(F)]
    for v in range(n): dp[1<<v][v]=1
    for m in range(1,F):
        for v in range(n):
            c=dp[m][v]
            if not c: continue
            for u in range(n):
                if not m>>u&1 and ok[v][u]: dp[m|1<<u][u]+=c
    return sum(dp[F-1])

if __name__=='__main__':
    print(sol(sys.stdin.read()))
