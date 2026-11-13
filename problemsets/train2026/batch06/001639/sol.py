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
    t=list(map(int,s.split())); m,X=t[0],t[1]; c=t[2:2+m]
    dp=[0]*(X+1); dp[0]=1
    for v in c:
        for x in range(v,X+1): dp[x]=(dp[x]+dp[x-v])%M
    return dp[X]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
