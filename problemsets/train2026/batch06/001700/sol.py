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
    t=list(map(int,s.split())); n,C=t[0],t[1]; w=t[2:2+n]; F=1<<n
    INF=(10**9,0); dp=[INF]*F; dp[0]=(1,0)
    for m in range(F):
        r0,l0=dp[m]
        if r0>=10**9: continue
        for i in range(n):
            if not m>>i&1:
                nx=(r0,l0+w[i]) if l0+w[i]<=C else (r0+1,w[i])
                if nx<dp[m|1<<i]: dp[m|1<<i]=nx
    return dp[F-1][0]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
