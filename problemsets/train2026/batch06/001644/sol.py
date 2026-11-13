import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def sol(s):
    n,k=map(int,s.split()); f=[1]+[0]*(k-1)
    for _ in range(n):
        g=[0]*k; g[0]=sum(f)%M
        for j in range(1,k): g[j]=f[j-1]
        f=g
    return sum(f)%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
