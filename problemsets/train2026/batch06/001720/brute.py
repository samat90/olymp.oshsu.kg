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
    n,m=map(int,s.split())
    def go(i,j):
        if i==n and j==m: return 1
        t=0
        if i<n: t+=go(i+1,j)
        if j<m: t+=go(i,j+1)
        if i<n and j<m: t+=go(i+1,j+1)
        return t
    return go(0,0)%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
