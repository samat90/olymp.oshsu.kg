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
    t=list(map(int,s.split())); a=t[1:1+t[0]]; n=len(a); best=1
    for m in range(1,1<<n):
        v=[a[i] for i in range(n) if m>>i&1]
        if len(v)<=best: continue
        d=[v[i+1]-v[i] for i in range(len(v)-1)]
        if all(x!=0 for x in d) and all(d[i]*d[i+1]<0 for i in range(len(d)-1)): best=len(v)
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
