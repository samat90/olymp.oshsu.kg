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
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]; c=0
    for x in range(1,1<<n):
        pr=1
        for i in range(n):
            if x>>i&1: pr*=a[i]
        if all(pr%(p*p) for p in (2,3,5,7,11,13,17,19,23,29)): c+=1
    return c%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
