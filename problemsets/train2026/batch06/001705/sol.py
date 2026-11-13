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
    t=list(map(int,s.split())); n,m=t[0],t[1]; p=2; ms=[]
    for _ in range(m):
        c=t[p]; mk=0
        for x in t[p+1:p+1+c]: mk|=1<<(x-1)
        ms.append(mk); p+=1+c
    INF=99; dp=[INF]*(1<<n); dp[0]=0
    for x in range(1<<n):
        if dp[x]==INF: continue
        for mk in ms:
            y=x|mk
            if dp[x]+1<dp[y]: dp[y]=dp[x]+1
    return dp[-1] if dp[-1]<INF else -1

if __name__=='__main__':
    print(sol(sys.stdin.read()))
