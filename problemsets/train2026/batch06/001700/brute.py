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
    t=list(map(int,s.split())); n,C=t[0],t[1]; w=t[2:2+n]; best=[n]
    bins=[]
    def go(i):
        if len(bins)>=best[0]: return
        if i==n: best[0]=len(bins); return
        for b in range(len(bins)):
            if bins[b]+w[i]<=C:
                bins[b]+=w[i]; go(i+1); bins[b]-=w[i]
        bins.append(w[i]); go(i+1); bins.pop()
    go(0)
    return best[0]

if __name__=='__main__':
    print(brute(sys.stdin.read()))
