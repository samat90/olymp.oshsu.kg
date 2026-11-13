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
    t=s.split(); w=t[0]; d=int(t[1]); ws=t[2:2+d]; n=len(w)
    dp=[0]*(n+1); dp[0]=1
    for i in range(1,n+1):
        a=0
        for x in ws:
            l=len(x)
            if l<=i and w.startswith(x,i-l): a+=dp[i-l]
        dp[i]=a%M
    return dp[n]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
