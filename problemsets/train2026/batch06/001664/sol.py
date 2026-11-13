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
    p,t=s.split()[:2]; n,m=len(p),len(t)
    dp=[False]*(m+1); dp[0]=True
    for i in range(1,n+1):
        c=p[i-1]; new=[False]*(m+1)
        if c=='*':
            new[0]=dp[0]
            for j in range(1,m+1): new[j]=new[j-1] or dp[j]
        else:
            for j in range(1,m+1):
                new[j]=dp[j-1] and (c=='?' or c==t[j-1])
        dp=new
    return "YES" if dp[m] else "NO"

if __name__=='__main__':
    print(sol(sys.stdin.read()))
