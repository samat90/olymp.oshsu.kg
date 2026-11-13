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
    t=list(map(int,s.split())); n=t[0]; w=t[1:1+n]; g=[[] for _ in range(n)]
    for i in range(n-1):
        a,b=t[1+n+2*i]-1,t[2+n+2*i]-1; g[a].append(b); g[b].append(a)
    par=[-1]*n; order=[0]; seen=[False]*n; seen[0]=True
    for v in order:
        for u in g[v]:
            if not seen[u]: seen[u]=True; par[u]=v; order.append(u)
    take=w[:]; skip=[0]*n
    for v in reversed(order):
        p=par[v]
        if p>=0:
            take[p]+=skip[v]; skip[p]+=max(take[v],skip[v])
    return max(take[0],skip[0])

if __name__=='__main__':
    print(sol(sys.stdin.read()))
