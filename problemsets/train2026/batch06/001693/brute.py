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
    from itertools import permutations
    t=list(map(int,s.split())); Lg,m=t[0],t[1]; ps=t[2:2+m]; best=10**18
    for order in permutations(ps):
        cuts=[0,Lg]; tot=0
        for c in order:
            lo=max(x for x in cuts if x<c); hi=min(x for x in cuts if x>c)
            tot+=hi-lo; cuts.append(c)
        best=min(best,tot)
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
