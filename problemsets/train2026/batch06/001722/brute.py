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
    t=list(map(int,s.split())); n=t[0]; p=t[1:1+n]
    def go(i,state,blocked):
        if i==n: return 0
        best=go(i+1,state,False)
        if state==0 and not blocked: best=max(best,-p[i]+go(i+1,1,False))
        if state==1: best=max(best,p[i]+go(i+1,0,True))
        return best
    return go(0,0,False)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
