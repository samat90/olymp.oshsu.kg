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
    t=list(map(int,s.split())); n,m=t[0],t[1]; a=t[2:]
    def go(i,j):
        if i==n-1 and j==m-1: return a[i*m+j]
        b=10**18
        if i+1<n: b=min(b,go(i+1,j))
        if j+1<m: b=min(b,go(i,j+1))
        return a[i*m+j]+b
    return go(0,0)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
