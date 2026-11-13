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
    t=list(map(int,s.split())); n,m,K=t[:3]; a=t[3:]
    prev=[[0]*K for _ in range(m)]
    for i in range(n):
        cur=[[0]*K for _ in range(m)]
        for j in range(m):
            v=a[i*m+j]%K
            if i==0 and j==0: cur[0][v]=1; continue
            for r in range(K):
                c=0
                if i: c+=prev[j][r]
                if j: c+=cur[j-1][r]
                if c: cur[j][(r+v)%K]=(cur[j][(r+v)%K]+c)%M
        prev=cur
    return prev[m-1][0]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
