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
    w=s.split()[0]; n=len(w)
    f=[[0]*n for _ in range(n)]
    for i in range(n-1,-1,-1):
        f[i][i]=1
        for j in range(i+1,n):
            b=f[i][j-1]+1
            for m in range(i,j):
                if w[m]==w[j]:
                    v=f[i][m]+(f[m+1][j-1] if m+1<=j-1 else 0)
                    if v<b: b=v
            f[i][j]=b
    return f[0][n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
