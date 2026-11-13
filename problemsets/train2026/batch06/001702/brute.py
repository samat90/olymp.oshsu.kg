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
    t=list(map(int,s.split())); n,m=t[0],t[1]; w=t[2:2+n]; E=[(t[2+n+2*i]-1,t[3+n+2*i]-1) for i in range(m)]; best=0
    for mk in range(1<<n):
        if any(mk>>a&1 and mk>>b&1 for a,b in E): continue
        best=max(best,sum(w[i] for i in range(n) if mk>>i&1))
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
