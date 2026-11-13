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
    t=list(map(int,s.split())); n,K=t[0],t[1]; p=t[2:2+n]
    def go(i,holding,left):
        if i==n: return 0
        best=go(i+1,holding,left)
        if holding is None:
            if left>0: best=max(best,go(i+1,p[i],left-1)-p[i])
        else: best=max(best,p[i]+go(i+1,None,left))
        return best
    return go(0,None,K)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
