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
    d=list(map(int,s.split()[0])); n=len(d)
    from functools import lru_cache
    @lru_cache(None)
    def f(pos,last,tight,started):
        if pos==n: return 1 if started else 0
        res=0; lim=d[pos] if tight else 9
        for x in range(lim+1):
            if started and x==last: continue
            ns=started or x>0
            res+=f(pos+1,x if ns else -1,tight and x==lim,ns)
        return res
    return f(0,-1,True,False)

if __name__=='__main__':
    print(sol(sys.stdin.read()))
