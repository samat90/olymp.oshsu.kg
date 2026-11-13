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
    t=list(map(int,s.split())); n=t[0]; c=[0]+t[1:1+n]+[0]
    def g(p):
        if p>=n+1: return 0 if p==n+1 else 10**18
        return min(c[p+1]+g(p+1), (c[p+2]+g(p+2)) if p+2<=n+1 else 10**18)
    return g(0)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
