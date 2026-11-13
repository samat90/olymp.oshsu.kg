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
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]; pre=[0]
    for x in a: pre.append(pre[-1]+x)
    INF=10**18; f=[[0]*n for _ in range(n)]
    for ln in range(2,n+1):
        for i in range(n-ln+1):
            j=i+ln-1
            f[i][j]=min(f[i][m]+f[m+1][j] for m in range(i,j))+pre[j+1]-pre[i]
    return f[0][n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
