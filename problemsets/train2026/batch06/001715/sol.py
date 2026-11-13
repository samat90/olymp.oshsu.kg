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
    t=list(map(int,s.split())); n,m=t[0],t[1]; a=t[2:]; INF=10**18
    nxt=[INF]*(m+1)
    for i in range(n-1,-1,-1):
        cur=[INF]*(m+1)
        for j in range(m-1,-1,-1):
            if i==n-1 and j==m-1: need=1
            else: need=min(nxt[j],cur[j+1])
            cur[j]=max(1,need-a[i*m+j])
        nxt=cur
    return nxt[0]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
