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
    t=list(map(int,s.split())); n=t[0]; g=[[] for _ in range(n)]
    for i in range(n-1):
        a,b=t[1+2*i]-1,t[2+2*i]-1; g[a].append(b); g[b].append(a)
    par=[-1]*n; order=[0]; seen=[False]*n; seen[0]=True
    for v in order:
        for u in g[v]:
            if not seen[u]: seen[u]=True; par[u]=v; order.append(u)
    INF=10**9
    a=[1]*n   # v has guard
    b=[0]*n   # v covered by a child (no guard on v)
    c=[0]*n   # v not covered yet (children all covered)
    ch=[[] for _ in range(n)]
    for v in order[1:]: ch[par[v]].append(v)
    for v in reversed(order):
        if not ch[v]:
            a[v]=1; b[v]=INF; c[v]=0
            continue
        a[v]=1+sum(min(a[u],b[u],c[u]) for u in ch[v])
        c[v]=sum(b[u] for u in ch[v])
        base=sum(min(a[u],b[u]) for u in ch[v])
        extra=min(max(0,a[u]-min(a[u],b[u])) for u in ch[v])
        b[v]=base+extra
    return min(a[0],b[0])

if __name__=='__main__':
    print(sol(sys.stdin.read()))
