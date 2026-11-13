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
    w=s.split()[0]; n=len(w); c=0
    for ctr in range(2*n-1):
        l=ctr//2; rr=l+ctr%2
        while l>=0 and rr<n and w[l]==w[rr]: c+=1; l-=1; rr+=1
    return c

if __name__=='__main__':
    print(sol(sys.stdin.read()))
