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
    t=list(map(int,s.split())); n,S0=t[0],t[1]; a=t[2:2+n]; dp=[0]*(S0+1); dp[0]=1
    for x in a:
        for c in range(S0,x-1,-1): dp[c]=(dp[c]+dp[c-x])%M
    return dp[S0]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
