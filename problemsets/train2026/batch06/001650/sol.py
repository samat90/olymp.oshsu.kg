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
    t=list(map(int,s.split())); a=t[1:1+t[0]]; n=len(a)
    ln=[1]*n; cn=[1]*n
    for i in range(n):
        ai=a[i]; bl=1; bc=1
        for j in range(i):
            if a[j]<ai:
                l=ln[j]+1
                if l>bl: bl=l; bc=cn[j]
                elif l==bl: bc+=cn[j]
        ln[i]=bl; cn[i]=bc%M
    mx=max(ln)
    return sum(cn[i] for i in range(n) if ln[i]==mx)%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
