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
    n=int(s.split()[0]); dp=[0]+[10**9]*n
    for x in range(1,n+1):
        j=1
        while j*j<=x:
            dp[x]=min(dp[x],dp[x-j*j]+1); j+=1
    return dp[n]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
