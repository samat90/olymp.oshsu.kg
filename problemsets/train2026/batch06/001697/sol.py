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
    t=list(map(int,s.split())); n=t[0]; c=[t[1+i*n:1+(i+1)*n] for i in range(n)]
    INF=10**18; dp=[INF]*(1<<n); dp[0]=0
    for m in range(1<<n):
        if dp[m]>=INF: continue
        i=bin(m).count('1')
        if i==n: continue
        for j in range(n):
            if not m>>j&1:
                v=dp[m]+c[i][j]
                if v<dp[m|1<<j]: dp[m|1<<j]=v
    return dp[-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
