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
    n,m=map(int,s.split()); c=0
    for x in range(1<<(n*m)):
        ok=True
        for i in range(n):
            for j in range(m):
                if x>>(i*m+j)&1:
                    if j+1<m and x>>(i*m+j+1)&1: ok=False
                    if i+1<n and x>>((i+1)*m+j)&1: ok=False
        if ok: c+=1
    return c%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
