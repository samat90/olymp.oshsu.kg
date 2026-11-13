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
    t=list(map(int,s.split())); n=t[0]; h=t[1:]
    dp=[0]*n
    for i in range(1,n):
        dp[i]=dp[i-1]+abs(h[i]-h[i-1])
        if i>=2: dp[i]=min(dp[i],dp[i-2]+abs(h[i]-h[i-2]))
    return dp[-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
