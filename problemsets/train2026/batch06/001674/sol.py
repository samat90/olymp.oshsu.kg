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
    t=list(map(int,s.split())); n,T=t[0],t[1]; a=t[2:2+n]; tot=sum(a)
    if abs(T)>tot or (tot+T)%2: return 0
    need=(tot+T)//2; dp=[0]*(need+1); dp[0]=1
    for x in a:
        for c in range(need,x-1,-1): dp[c]=(dp[c]+dp[c-x])%M
    return dp[need]%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
