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
    t=list(map(int,s.split())); n=t[0]; a=[t[1+i*n:1+(i+1)*n] for i in range(n)]
    paths=[]
    def go(i,j,cur):
        cur=cur+[(i,j)]
        if i==n-1 and j==n-1: paths.append(cur); return
        if i+1<n: go(i+1,j,cur)
        if j+1<n: go(i,j+1,cur)
    go(0,0,[])
    best=0
    for p in paths:
        for q in paths:
            cells=set(p)|set(q)
            best=max(best,sum(a[i][j] for i,j in cells))
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
