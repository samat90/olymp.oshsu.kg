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
    t=list(map(int,s.split())); n,m=t[0],t[1]; p=2; ms=[]
    for _ in range(m):
        c=t[p]; ms.append(set(t[p+1:p+1+c])); p+=1+c
    best=-1
    for x in range(1<<m):
        u=set()
        for i in range(m):
            if x>>i&1: u|=ms[i]
        if len(u)==n:
            c=bin(x).count('1')
            if best<0 or c<best: best=c
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
