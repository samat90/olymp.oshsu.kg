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
    a,b=s.split()[:2]; m=len(b)
    dp=[1]+[0]*m
    for x in a:
        for j in range(m,0,-1):
            if b[j-1]==x: dp[j]=(dp[j]+dp[j-1])%M
    return dp[m]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
