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
    t=list(map(int,s.split())); Lg,m=t[0],t[1]; p=[0]+sorted(t[2:2+m])+[Lg]
    f=[[0]*(m+2) for _ in range(m+2)]
    for ln in range(2,m+2):
        for i in range(m+2-ln):
            j=i+ln
            f[i][j]=min(f[i][c]+f[c][j] for c in range(i+1,j))+p[j]-p[i]
    return f[0][m+1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
