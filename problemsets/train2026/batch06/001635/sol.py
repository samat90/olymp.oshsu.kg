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
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]
    def rob(a):
        p=q=0
        for x in a: p,q=q,max(q,p+x)
        return q
    return a[0] if n==1 else max(rob(a[1:]),rob(a[:-1]))

if __name__=='__main__':
    print(sol(sys.stdin.read()))
