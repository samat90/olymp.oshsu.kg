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
    n=int(s.split()[0])
    sq=[j*j for j in range(1,int(n**.5)+1)]
    def can(rem,d,mn):
        if rem==0: return True
        if d==0: return False
        return any(q>=mn and can(rem-q,d-1,q) for q in sq if q<=rem)
    d=1
    while not can(n,d,0): d+=1
    return d

if __name__=='__main__':
    print(brute(sys.stdin.read()))
