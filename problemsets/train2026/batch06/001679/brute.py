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
    t=list(map(int,s.split())); g,W=t[0],t[1]; p=2; gr=[]
    for _ in range(g):
        c=t[p]; p+=1; gr.append([(t[p+2*i],t[p+2*i+1]) for i in range(c)]); p+=2*c
    def go(i,rem):
        if i==g: return 0
        best=go(i+1,rem)
        for w,v in gr[i]:
            if w<=rem: best=max(best,v+go(i+1,rem-w))
        return best
    return go(0,W)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
