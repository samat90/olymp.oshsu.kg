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
    n,m=map(int,s.split()); 
    dp={0:1}
    for c in range(m):
        for rr in range(n):
            nd={}
            for mask,v in dp.items():
                if mask>>rr&1:
                    nm=mask&~(1<<rr); nd[nm]=(nd.get(nm,0)+v)%M
                else:
                    nm=mask|1<<rr
                    if c+1<m: nd[nm]=(nd.get(nm,0)+v)%M
                    if rr+1<n and not mask>>(rr+1)&1:
                        nm=mask|1<<(rr+1)
                        nd[nm]=(nd.get(nm,0)+v)%M
            dp=nd
    return dp.get(0,0)%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
