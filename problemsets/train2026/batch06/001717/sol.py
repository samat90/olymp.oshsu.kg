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
    t=list(map(int,s.split())); n,m=t[0],t[1]; a=t[2:]
    order=sorted(range(n*m),key=lambda x:-a[x]); f=[1]*(n*m); best=1
    for c in order:
        i,j=divmod(c,m); b=1
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            x,y=i+di,j+dj
            if 0<=x<n and 0<=y<m and a[x*m+y]>a[c] and f[x*m+y]+1>b: b=f[x*m+y]+1
        f[c]=b
        if b>best: best=b
    return best

if __name__=='__main__':
    print(sol(sys.stdin.read()))
