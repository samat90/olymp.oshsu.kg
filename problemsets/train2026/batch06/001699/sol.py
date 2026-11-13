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
    t=list(map(int,s.split())); n,k=t[0],t[1]; a=t[2:2+n]; tot=sum(a)
    if tot%k: return "NO"
    T=tot//k
    if max(a)>T: return "NO"
    F=1<<n; dp=[-1]*F; dp[0]=0
    for m in range(F):
        if dp[m]<0: continue
        for i in range(n):
            if not m>>i&1 and dp[m]+a[i]<=T:
                nm=m|1<<i
                if dp[nm]<0: dp[nm]=(dp[m]+a[i])%T
    return "YES" if dp[F-1]==0 else "NO"

if __name__=='__main__':
    print(sol(sys.stdin.read()))
