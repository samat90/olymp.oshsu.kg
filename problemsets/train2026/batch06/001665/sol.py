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
    dp=[[False]*(m+1) for _ in range(n+1)]; dp[n][m]=True
    for i in range(n-1,-1,-1):
        star=i+1<n and p[i+1]=='*'
        for j in range(m,-1,-1):
            first=j<m and (p[i]=='.' or p[i]==t[j])
            if star: dp[i][j]=dp[i+2][j] or (first and dp[i][j+1])
            else: dp[i][j]=first and dp[i+1][j+1]
    return "YES" if dp[0][0] else "NO"

if __name__=='__main__':
    print(sol(sys.stdin.read()))
