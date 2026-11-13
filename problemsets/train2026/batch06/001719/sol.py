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
    n,r0,c0,K=map(int,s.split()); mv=[(1,2),(2,1),(-1,2),(-2,1),(1,-2),(2,-1),(-1,-2),(-2,-1)]
    f=[[1]*n for _ in range(n)]
    for _ in range(K):
        g=[[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                t=0
                for di,dj in mv:
                    x,y=i+di,j+dj
                    if 0<=x<n and 0<=y<n: t+=f[x][y]
                g[i][j]=t%M
        f=g
    return f[r0-1][c0-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
