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
    t=list(map(int,s.split())); n,W=t[0],t[1]; dp=[0]*(W+1)
    for i in range(n):
        w,v=t[2+2*i],t[3+2*i]
        for c in range(W,w-1,-1):
            if dp[c-w]+v>dp[c]: dp[c]=dp[c-w]+v
    return dp[W]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
