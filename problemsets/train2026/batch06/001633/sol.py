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
    t=list(map(int,s.split())); n,k=t[0],t[1]; h=t[2:2+n]
    dp=[10**18]*n; dp[0]=0
    for i in range(1,n):
        hi=h[i]
        dp[i]=min(dp[j]+abs(h[j]-hi) for j in range(max(0,i-k),i))
    return dp[-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
