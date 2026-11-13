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
    t=list(map(int,s.split())); n=t[0]; a=[t[1+i*n:1+(i+1)*n] for i in range(n)]
    NEG=-1; dp=[[NEG]*n for _ in range(n)]; dp[0][0]=a[0][0]
    for st in range(1,2*n-1):
        nd=[[NEG]*n for _ in range(n)]
        for x1 in range(n):
            y1=st-x1
            if not 0<=y1<n: continue
            for x2 in range(n):
                y2=st-x2
                if not 0<=y2<n: continue
                b=NEG
                for p1 in (x1,x1-1):
                    for p2 in (x2,x2-1):
                        if 0<=p1<n and 0<=p2<n and dp[p1][p2]>b: b=dp[p1][p2]
                if b<0: continue
                v=a[x1][y1]+(a[x2][y2] if x1!=x2 else 0)
                nd[x1][x2]=b+v
        dp=nd
    return dp[n-1][n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
