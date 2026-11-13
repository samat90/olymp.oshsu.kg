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
    t=list(map(int,s.split())); n=t[0]; E=[(t[1+2*i]-1,t[2+2*i]-1) for i in range(n-1)]
    nb=[1<<i for i in range(n)]
    for a,b in E: nb[a]|=1<<b; nb[b]|=1<<a
    best=n
    for m in range(1<<n):
        cov=0
        for i in range(n):
            if m>>i&1: cov|=nb[i]
        if cov==(1<<n)-1: best=min(best,bin(m).count('1'))
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
