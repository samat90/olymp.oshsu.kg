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
    e=s.split()[0]; v=e[0::2]; op=e[1::2]; n=len(v)
    T=[[0]*n for _ in range(n)]; F=[[0]*n for _ in range(n)]
    for i in range(n):
        T[i][i]=int(v[i]=='T'); F[i][i]=int(v[i]=='F')
    for ln in range(2,n+1):
        for i in range(n-ln+1):
            j=i+ln-1; t=f=0
            for m in range(i,j):
                a,b,c,d=T[i][m],F[i][m],T[m+1][j],F[m+1][j]; o=op[m]
                tot=(a+b)*(c+d)
                if o=='&': tt=a*c
                elif o=='|': tt=tot-b*d
                else: tt=a*d+b*c
                t+=tt; f+=tot-tt
            T[i][j]=t%M; F[i][j]=f%M
    return T[0][n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
