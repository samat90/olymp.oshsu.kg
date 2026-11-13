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
    t=list(map(int,s.split())); n=t[0]; f=t[1:1+n]; pre=[0]
    for x in f: pre.append(pre[-1]+x)
    INF=10**18; d=[[0]*(n+2) for _ in range(n+2)]
    for ln in range(1,n+1):
        for i in range(n-ln+1):
            j=i+ln-1; b=INF
            for r_ in range(i,j+1):
                v=(d[i][r_-1] if r_>i else 0)+(d[r_+1][j] if r_<j else 0)
                if v<b: b=v
            d[i][j]=b+pre[j+1]-pre[i]
    return d[0][n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
