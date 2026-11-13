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
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]
    def go(lst):
        if not lst: return 0
        best=0
        for i in range(len(lst)):
            l=lst[i-1] if i>0 else 1; rr=lst[i+1] if i+1<len(lst) else 1
            best=max(best,l*lst[i]*rr+go(lst[:i]+lst[i+1:]))
        return best
    return go(a)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
