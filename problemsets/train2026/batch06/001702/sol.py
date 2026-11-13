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
    t=list(map(int,s.split())); n,m=t[0],t[1]; w=t[2:2+n]; adj=[0]*n
    for i in range(m):
        a,b=t[2+n+2*i]-1,t[3+n+2*i]-1; adj[a]|=1<<b; adj[b]|=1<<a
    dp=[0]*(1<<n)
    for mk in range(1,1<<n):
        v=(mk&-mk).bit_length()-1; rest=mk&(mk-1)
        dp[mk]=max(dp[rest],w[v]+dp[rest&~adj[v]])
    return dp[-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
