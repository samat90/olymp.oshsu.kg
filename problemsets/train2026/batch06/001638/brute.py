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
    t=list(map(int,s.split())); m,X=t[0],t[1]; c=t[2:2+m]
    best=[10**9]
    def go(i,rem,cnt):
        if rem==0: best[0]=min(best[0],cnt); return
        if i==m: return
        for q in range(rem//c[i]+1): go(i+1,rem-q*c[i],cnt+q)
    go(0,X,0)
    return best[0] if best[0]<10**9 else -1

if __name__=='__main__':
    print(brute(sys.stdin.read()))
