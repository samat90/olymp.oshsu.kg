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
    t=list(map(int,s.split())); n=t[0]; d=[t[1+i*n:1+(i+1)*n] for i in range(n)]
    INF=10**18; F=1<<n; dp=[[INF]*n for _ in range(F)]; dp[1][0]=0
    for m in range(1,F,2):
        row=dp[m]
        for v in range(n):
            c=row[v]
            if c>=INF: continue
            for u in range(1,n):
                if not m>>u&1:
                    nm=m|1<<u
                    if c+d[v][u]<dp[nm][u]: dp[nm][u]=c+d[v][u]
    return min(dp[F-1][v]+d[v][0] for v in range(1,n))

if __name__=='__main__':
    print(sol(sys.stdin.read()))
