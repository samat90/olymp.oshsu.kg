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
    t=s.split(); n=int(t[0]); ws=t[1:1+n]
    def pred(x,y):
        return len(y)==len(x)+1 and any(y[:i]+y[i+1:]==x for i in range(len(y)))
    best=[1]
    def go(w,d):
        best[0]=max(best[0],d)
        for y in ws:
            if pred(w,y): go(y,d+1)
    for w in ws: go(w,1)
    return best[0]

if __name__=='__main__':
    print(brute(sys.stdin.read()))
