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
    t=s.split(); n=int(t[0]); ws=t[1:1+n]; best=0
    for x in range(1<<n):
        j=''.join(ws[i] for i in range(n) if x>>i&1)
        if len(set(j))==len(j): best=max(best,len(j))
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
