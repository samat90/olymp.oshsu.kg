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
    t=list(map(int,s.split())); a=t[1:1+t[0]]; vs=sorted(set(a)); best=0
    for m in range(1<<len(vs)):
        ch={vs[i] for i in range(len(vs)) if m>>i&1}
        if any(v+1 in ch for v in ch): continue
        best=max(best,sum(x for x in a if x in ch))
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
