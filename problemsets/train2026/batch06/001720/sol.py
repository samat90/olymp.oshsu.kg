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
    n,m=map(int,s.split()); prev=[1]*(m+1)
    for i in range(1,n+1):
        cur=[1]+[0]*m
        for j in range(1,m+1): cur[j]=(prev[j]+cur[j-1]+prev[j-1])%M
        prev=cur
    return prev[m]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
