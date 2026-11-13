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
    t=list(map(int,s.split())); n=t[0]; h=t[1:]
    best=[10**18]
    def go(i,c):
        if i==n-1: best[0]=min(best[0],c); return
        for d in (1,2):
            if i+d<n: go(i+d,c+abs(h[i]-h[i+d]))
    go(0,0); return best[0]

if __name__=='__main__':
    print(brute(sys.stdin.read()))
