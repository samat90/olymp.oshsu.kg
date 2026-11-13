import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def brute(s):
    n,m=map(int,s.split()); g=[[0]*m for _ in range(n)]
    def go(p):
        while p<n*m and g[p//m][p%m]: p+=1
        if p==n*m: return 1
        r,c=p//m,p%m; t=0
        g[r][c]=1
        if c+1<m and not g[r][c+1]: g[r][c+1]=1; t+=go(p+1); g[r][c+1]=0
        if r+1<n and not g[r+1][c]: g[r+1][c]=1; t+=go(p+1); g[r+1][c]=0
        g[r][c]=0
        return t
    return go(0)%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
