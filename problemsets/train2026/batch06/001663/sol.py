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
    a,b,c=s.split()[:3]; n,m=len(a),len(b)
    if n+m!=len(c): return "NO"
    dp=[False]*(m+1); dp[0]=True
    for i in range(n+1):
        for j in range(m+1):
            if i==0 and j==0: continue
            ok=False
            if i>0 and dp[j] and a[i-1]==c[i+j-1]: ok=True
            if j>0 and dp[j-1] and b[j-1]==c[i+j-1]: ok=True
            dp[j]=ok
    return "YES" if dp[m] else "NO"

if __name__=='__main__':
    print(sol(sys.stdin.read()))
